SECRET_KEY = "fake-key"  # nosec
INSTALLED_APPS = ["tests", "django.contrib.auth", "django.contrib.contenttypes"]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "pbx2",
        "USER": "pbx2",
        "PASSWORD": "pbx2",
        "HOST": "localhost",
        "PORT": 5432,
    }
}
