import smtplib
from django.conf import settings

from authlib.integrations.base_client import OAuthError
from authlib.jose import jwt
from authlib.oidc.core import CodeIDToken
from django.contrib.auth import logout, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.permissions import AllowAny

from jcourse.throttles import EmailCodeRateThrottle, VerifyAuthRateThrottle
from oauth.utils import *


@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
@csrf_exempt
def auth_logout(request):
    logout(request)
    return JsonResponse({'detail': '已登出。'})


@api_view(['POST'])
@throttle_classes([VerifyAuthRateThrottle])
@permission_classes([AllowAny])
@csrf_exempt
def auth_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if username is None or password is None:
        return JsonResponse({'detail': '参数错误。'}, status=400)
    
    # 获取客户端IP
    client_ip = get_client_ip(request)
    
    # 检查登录尝试次数限制（IP + 用户名）
    if not login_attempt_verify_times(client_ip, username):
        return JsonResponse({'detail': '登录尝试过于频繁，请30分钟后重试。'}, status=429)
    
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'detail': '用户名或密码错误。'}, status=400)
    
    # 登录成功，清除失败记录
    clean_login_attempt(client_ip, username)
    login(request, user)
    clean_email_code(username)
    return JsonResponse({'account': username})


def login_jaccount(request):
    redirect_uri = request.GET.get('redirect_uri', '')
    if redirect_uri == '':
        redirect_uri = request.build_absolute_uri(reverse('auth_jaccount'))
    return jaccount.authorize_redirect(request, redirect_uri)


def auth_jaccount(request):
    try:
        token = jaccount.authorize_access_token(request)
    except OAuthError:
        return JsonResponse({'detail': '参数错误。'}, status=400)
    claims = jwt.decode(token.get('id_token'),
                        jaccount.client_secret, claims_cls=CodeIDToken)
    user_type = claims['type']
    account = claims['sub']
    login_with(request, account, user_type)
    response = JsonResponse({'account': account})
    return response


def sync_lessons_login(request):
    redirect_uri = request.GET.get('redirect_uri', '')
    if redirect_uri == '':
        redirect_uri = request.build_absolute_uri(reverse('sync-lessons-auth'))
    return jaccount.authorize_redirect(request, redirect_uri, scope="basic lessons")


def sync_lessons_auth(request):
    try:
        token = jaccount.authorize_access_token(request)
    except OAuthError:
        return JsonResponse({'detail': '参数错误。'}, status=400)
    request.session['token'] = token
    return JsonResponse({'detail': '同步状态就绪。'})


@api_view(['POST'])
@throttle_classes([EmailCodeRateThrottle])
@permission_classes([AllowAny])
@csrf_exempt
def auth_email_send_code(request):
    """邮箱验证码发送接口 - 仅用于注册"""
    from django.contrib.auth.models import User
    
    account: str = request.data.get("account", None)
    if account is None:
        return JsonResponse({'detail': '参数错误。'}, status=400)
    account = account.strip().lower()
    
    # 检查账号是否已注册
    former_username = hash_username(request.data.get("account", "").strip())  # 原始大小写
    username = hash_username(account)  # 小写
    
    # 检查是否已经存在用户（包括旧格式和新格式）
    user_exists = (User.objects.filter(username=former_username).exists() or 
                   User.objects.filter(username=username).exists())
    
    if user_exists:
        return JsonResponse({'detail': '该账号已注册，请直接登录。如忘记密码，请使用忘记密码功能。'}, status=400)
    
    if not settings.EMAIL_ACCOUNT_DOMAIN:
        return JsonResponse({'detail': '注册邮箱尚未配置，请联系管理员。'}, status=503)

    try:
        code = generate_code()
        auth_store_email_code(account, code)
        if send_code_email(account + "@" + settings.EMAIL_ACCOUNT_DOMAIN, code):
            return JsonResponse({'detail': '邮件已发送！请查看学生邮箱收件箱（包括垃圾邮件）。'})
    except smtplib.SMTPDataError:
        pass
    return JsonResponse({'detail': '验证码发送失败，请稍后重试。'}, status=500)


@api_view(['POST'])
@throttle_classes([VerifyAuthRateThrottle])
@permission_classes([AllowAny])
@csrf_exempt
def auth_email_verify_code(request):
    """邮箱验证码验证接口 - 暂时禁用登录，仅用于注册"""
    return JsonResponse({'detail': '邮箱验证登录功能暂时关闭，请使用其他登录方式。'}, status=503)


@api_view(['POST'])
@throttle_classes([VerifyAuthRateThrottle])
@permission_classes([AllowAny])
@csrf_exempt
def auth_email_register(request):
    """邮箱验证注册接口 - 验证邮箱验证码并设置密码完成注册"""
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    
    account: str = request.data.get("account", None)
    code: str = request.data.get("code", None)
    password: str = request.data.get("password", None)
    username: str = request.data.get("username", None)
    
    if account is None or code is None or password is None or username is None:
        return JsonResponse({'detail': '参数错误。'}, status=400)
    
    account = account.strip().lower()
    code = code.strip()
    username = username.strip()
    
    # 验证用户名格式
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', username) or len(username) < 3 or len(username) > 20:
        return JsonResponse({'detail': '用户名格式不正确，应为3-20位字母、数字或下划线。'}, status=400)
    
    # 检查用户名是否已存在
    if User.objects.filter(username=username).exists():
        return JsonResponse({'detail': '用户名已被使用，请选择其他用户名。'}, status=400)
    
    if not auth_verify_times(account):
        return JsonResponse({'detail': '尝试次数达到上限，请稍后重试。'}, status=429)
    
    if not auth_verify_email_code(account, code):
        return JsonResponse({'detail': '验证码错误，请重试。'}, status=400)
    
    # 验证密码强度
    try:
        validate_password(password)
    except ValidationError as e:
        return JsonResponse({'detail': f'密码不符合要求：{"; ".join(e.messages)}'}, status=400)
    
    # 创建用户并设置密码和用户名
    user = User.objects.create_user(username=username, password=password)
    
    # 创建用户profile，关联学生证号码
    from oauth.models import UserProfile
    UserProfile.objects.create(user=user, account=account, lowercase=True)
    
    # 登录用户
    login(request, user)
    clean_email_code(account)
    
    response = JsonResponse({'account': username, 'message': '注册成功！'})
    return response


@api_view(['POST'])
@throttle_classes([VerifyAuthRateThrottle])
@permission_classes([AllowAny])
@csrf_exempt
def auth_email_verify_password(request):
    account = request.data.get('account')
    password = request.data.get('password')

    if account is None or password is None:
        return JsonResponse({'detail': '参数错误。'}, status=400)
    account = account.strip().lower()
    password = password.strip()

    # 获取客户端IP
    client_ip = get_client_ip(request)
    
    # 检查登录尝试次数限制（IP + 学生证号码）
    if not login_attempt_verify_times(client_ip, account):
        return JsonResponse({'detail': '登录尝试过于频繁，请30分钟后重试。'}, status=429)

    # 尝试通过学生证号码查找用户
    from oauth.models import UserProfile
    try:
        user_profile = UserProfile.objects.get(account=account)
        user = authenticate(request, username=user_profile.user.username, password=password)
    except UserProfile.DoesNotExist:
        # 兼容旧用户，尝试使用哈希用户名
        username = hash_username(account)
        user = authenticate(request, username=username, password=password)
    
    if user is None:
        return JsonResponse({'detail': '邮箱或者密码错误。'}, status=400)

    # 登录成功，清除失败记录
    clean_login_attempt(client_ip, account)
    login(request, user)
    clean_email_code(account)
    return JsonResponse({'account': account})


@api_view(['POST'])
@throttle_classes([EmailCodeRateThrottle])
def reset_password_send_code(request):
    account: str = request.data.get("account", None)
    if account is None:
        return JsonResponse({'detail': '参数错误。'}, status=400)
    account = account.strip().lower()
    if request.user.username != hash_username(account):
        return JsonResponse({'detail': '请输入本账号对应的邮箱！'}, status=400)
    if not settings.EMAIL_ACCOUNT_DOMAIN:
        return JsonResponse({'detail': '注册邮箱尚未配置，请联系管理员。'}, status=503)
    try:
        code = generate_code()
        reset_store_email_code(account, code)
        if reset_send_code_email(account + "@" + settings.EMAIL_ACCOUNT_DOMAIN, code):
            return JsonResponse({'detail': '邮件已发送！请查看学生邮箱收件箱（包括垃圾邮件）。'})
    except smtplib.SMTPDataError:
        pass
    return JsonResponse({'detail': '验证码发送失败，请稍后重试。'}, status=500)


@api_view(['POST'])
@throttle_classes([VerifyAuthRateThrottle])
def reset_password_reset(request):
    account: str = request.data.get("account", None)
    code: str = request.data.get("code", None)
    password: str = request.data.get("password", None)
    if account is None or code is None or password is None:
        return JsonResponse({'detail': '参数错误。'}, status=400)
    account = account.strip().lower()
    if request.user.username != hash_username(account):
        return JsonResponse({'detail': '请输入本账号对应的邮箱！'}, status=400)
    if not reset_verify_email_code(account, code):
        return JsonResponse({'detail': '验证码错误，请重试。'}, status=400)
    try:
        validate_password(password, request.user)
    except ValidationError:
        return JsonResponse({'detail': "密码太弱！请至少9位长度，包含字母和数字，并且不是常见密码。"}, status=400)
    reset_clean_email_code(account)
    request.user.set_password(password)
    request.user.save()
    return JsonResponse({"detail": "更改密码成功。"})
