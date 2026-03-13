SECRET_KEY = "test-secret-key-not-for-production"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.admin",
    "cms",
    "menus",
    "treebeard",
    "djangocms_markdown",
    "tests",
]

SITE_ID = 1

LANGUAGES = [("en", "English")]
LANGUAGE_CODE = "en"

CMS_CONFIRM_VERSION4 = True

CMS_LANGUAGES = {
    1: [{"code": "en", "name": "English"}],
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ROOT_URLCONF = "tests.urls"

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
