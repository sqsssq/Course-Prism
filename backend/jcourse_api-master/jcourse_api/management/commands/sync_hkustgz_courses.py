"""Import public course listings from the HKUST(GZ) SISN course query page."""

import time

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from jcourse_api.models import Course, CourseOffering, Department, Semester, Teacher


SIS_API = 'https://sisn-service.hkust-gz.edu.cn'
TERMS_PATH = '/api/tHkustgzTermInfo/term/listPublicMarketTermInfo'
COURSES_PATH = '/api/course/pageCourseSupermarkeView'


def primary_instructors(section):
    instructors = {}
    for meeting in section.get('meetingInfoList') or []:
        for person in meeting.get('instructorList') or []:
            if person.get('instructorRoleInd') != 'PI':
                continue
            name = (person.get('instructorName') or '').strip()
            if name:
                key = person.get('staffId') or name
                instructors[key] = {'tid': person.get('staffId') or None, 'name': name}
    return list(instructors.values()) or [{'tid': None, 'name': 'TBA'}]


def public_meetings(section):
    return [
        {
            'start_date': meeting.get('startDate'),
            'end_date': meeting.get('endDate'),
            'week_day': meeting.get('weekDay'),
            'start_time': meeting.get('meetingStartTime'),
            'end_time': meeting.get('meetingEndTime'),
            'location': meeting.get('facilityName'),
        }
        for meeting in section.get('meetingInfoList') or []
    ]


class Command(BaseCommand):
    help = 'Sync public HKUST(GZ) course, instructor and section data for one term.'

    def add_arguments(self, parser):
        parser.add_argument('--term-id', help='SIS term ID; defaults to the first public term')
        parser.add_argument('--page-size', type=int, default=100)
        parser.add_argument('--limit-pages', type=int, help='For a small trial import')
        parser.add_argument('--dry-run', action='store_true', help='Fetch and validate without writing')

    def post(self, session, path, payload):
        try:
            response = session.post(SIS_API + path, json=payload, timeout=30)
            response.raise_for_status()
            body = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise CommandError(f'SIS request failed: {exc}') from exc
        if body.get('code') != '0':
            raise CommandError(f'SIS returned: {body.get("message", "unknown error")}')
        return body

    def handle(self, *args, **options):
        page_size = options['page_size']
        if not 1 <= page_size <= 100:
            raise CommandError('--page-size must be between 1 and 100')
        if options['limit_pages'] is not None and options['limit_pages'] < 1:
            raise CommandError('--limit-pages must be positive')

        with requests.Session() as session:
            session.headers.update({'User-Agent': 'HKUSTGZCourseReview/1.0 (public course sync)'})
            terms = self.post(session, TERMS_PATH, {}).get('data', {}).get('termList') or []
            term = next((item for item in terms if item.get('termId') == options['term_id']), None) if options['term_id'] else next(iter(terms), None)
            if not term:
                raise CommandError('Requested term is not in the public SIS term list')
            term_id = term['termId']
            term_name = term['description']
            self.stdout.write(f'Syncing {term_name} ({term_id})')

            page = 1
            course_count = section_count = 0
            while True:
                body = self.post(session, COURSES_PATH, {'termId': term_id, 'pageIndex': page, 'pageSize': page_size})
                rows = body.get('data') or []
                if not isinstance(rows, list):
                    raise CommandError('Unexpected SIS course response')
                if not options['dry_run']:
                    with transaction.atomic():
                        semester, _ = Semester.objects.get_or_create(name=term_name)
                        for row in rows:
                            section_count += self.import_row(row, semester)
                else:
                    section_count += sum(len(row.get('classSections') or []) for row in rows)
                course_count += len(rows)
                self.stdout.write(f'Page {page}: {len(rows)} courses')
                if len(rows) < page_size or (options['limit_pages'] and page >= options['limit_pages']):
                    break
                page += 1
                time.sleep(0.3)

        self.stdout.write(self.style.SUCCESS(f'{course_count} course records, {section_count} sections; dry_run={options["dry_run"]}'))

    def import_row(self, row, semester):
        info = row.get('courseInfo') or {}
        code = (info.get('crseCode') or '').strip()
        if not code:
            return 0
        subject = (info.get('subject') or code[:4]).strip()
        department, _ = Department.objects.get_or_create(name=subject[:64])
        name = (info.get('crseShortDesc') or info.get('crseName') or code).strip()[:255]
        credit = float(info.get('totalCredits') or 0)
        sections = row.get('classSections') or []

        for section in sections:
            people = primary_instructors(section)
            teachers = []
            for person in people:
                if person['tid']:
                    teacher, _ = Teacher.objects.update_or_create(
                        tid=person['tid'], defaults={'name': person['name'], 'department': department, 'last_semester': semester}
                    )
                else:
                    teacher, _ = Teacher.objects.get_or_create(name=person['name'], tid=None, defaults={'department': department})
                teachers.append(teacher)

            for teacher in teachers:
                course, _ = Course.objects.update_or_create(
                    code=code, main_teacher=teacher,
                    defaults={'name': name, 'credit': credit, 'department': department, 'last_semester': semester},
                )
                course.teacher_group.set(teachers)
                source_id = section.get('classId') or f'{semester.name}:{code}:{section.get("classSection", "")}'
                CourseOffering.objects.update_or_create(
                    source_class_id=source_id, course=course,
                    defaults={
                        'semester': semester,
                        'section': (section.get('classSection') or '')[:32],
                        'class_number': (section.get('classNbr') or '')[:32],
                        'meetings': public_meetings(section),
                    },
                )
        return len(sections)
