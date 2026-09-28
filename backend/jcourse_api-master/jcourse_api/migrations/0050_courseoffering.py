from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('jcourse_api', '0049_teammember_website')]

    operations = [
        migrations.CreateModel(
            name='CourseOffering',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_class_id', models.CharField(max_length=64)),
                ('section', models.CharField(max_length=32)),
                ('class_number', models.CharField(blank=True, max_length=32)),
                ('meetings', models.JSONField(blank=True, default=list)),
                ('last_synced_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offerings', to='jcourse_api.course')),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offerings', to='jcourse_api.semester')),
            ],
            options={
                'ordering': ['-semester__name', 'course__code', 'section'],
                'indexes': [models.Index(fields=['semester', 'course'], name='jc_off_sem_course_idx')],
                'constraints': [models.UniqueConstraint(fields=('source_class_id', 'course'), name='unique_sis_offering')],
            },
        ),
    ]
