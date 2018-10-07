import os
import raven

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '$3mrpu&r)^f3gz4-1%b-kx7(w(e&31y5m!_i+u==!%ksj4$nv#'
DEBUG = True

##### 새팅 상태 위에서 먼저 정의 #####
# 민감한 정보 불러오기: 아이피 주소
testing = os.environ.get('TRAVIS', 'False')  # Travis에서 작동하는지 확인
###############################

IP_ADDRESS = '207.148.99.218'
CACHE_IP = '198.13.60.19'

ALLOWED_HOSTS = ['127.0.0.1', '127.0.1.1', IP_ADDRESS, CACHE_IP]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # corsheaders
    'corsheaders',

    # celery + celerybeat
    'django_celery_beat',
    'django_celery_results',

    # Django Rest Framework
    'rest_framework',
    'rest_framework.authtoken',

    # Sentry
    'raven.contrib.django.raven_compat',

    # 마인드 앱
    'algorithms',
    'api',
]

# Sentry 새팅 정의내리는 곳, DSN으로 들어가면 에러 로깅된 것이 확인가능
RAVEN_CONFIG = {
    'dsn': 'https://662a9e2e3cae438e804835019447ebd4:9e03f7087f7348d4a0c619529f7f9db9@sentry.io/1248595',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(BASE_DIR),
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mined.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mined.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ko-KR'  # http://www.i18nguy.com/unicode/language-identifiers.html
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_L10N = True
USE_TZ = False

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_ALLOW_ALL = True  # 외부에서 API 요청 가능하도록 새팅
