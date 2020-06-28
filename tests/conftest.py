import os
import pytest

import django
from django.conf import settings
from django.db import connection


def pytest_configure():
    test_db = os.environ.get("TEST_DB", "sqlite")
    installed_apps = [
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "tests.generic",
        "tests.ambiguous",
        "tests.ambiguous2",
    ]
    db_username = ""
    db_password = ""
    if test_db == "sqlite":
        db_engine = "django.db.backends.sqlite3"
        db_name = ":memory:"
    elif test_db == "postgresql":
        db_engine = "django.db.backends.postgresql_psycopg2"
        db_name = "postgres"
        installed_apps = ["django.contrib.postgres"] + installed_apps
    elif test_db == "postgis":
        db_engine = "django.contrib.gis.db.backends.postgis"
        db_name = "test"
        db_username = "user1"
        db_password = "pwd1"
        installed_apps = [
            "django.contrib.postgres",
            "django.contrib.gis",
        ] + installed_apps
    else:
        raise NotImplementedError("Tests for % are not supported", test_db)

    settings.configure(
        DATABASES={"default": {"ENGINE": db_engine, "NAME": db_name,
                               "USER": db_username, "PASSWORD": db_password, "HOST": "127.0.0.1"}},
        INSTALLED_APPS=installed_apps,
        LANGUAGE_CODE="en",
        SITE_ID=1,
        MIDDLEWARE=(),
        USE_TZ=os.environ.get("USE_TZ", False),
    )

    from model_bakery import baker

    def gen_same_text():
        return "always the same text"

    baker.generators.add("tests.generic.fields.CustomFieldViaSettings", gen_same_text)

    django.setup()


@pytest.fixture(scope='session')
def django_db_setup(django_db_blocker):
    with django_db_blocker.unblock():
        with connection.cursor() as c:
            c.execute('''create extension hstore;''')
            c.execute('''create extension postgis;''')
            c.execute('''create extension citext;''')
