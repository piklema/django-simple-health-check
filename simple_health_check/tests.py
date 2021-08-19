from django.test import TestCase, override_settings
from django.apps import apps


class SimpleTest(TestCase):
    def test_liveness(self):
        apps.get_app_config('simple_health_check').register_checks()

        response = self.client.get('/liveness/')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.content == b'ok')

    def test_readiness(self):
        apps.get_app_config('simple_health_check').register_checks()

        response = self.client.get('/readiness/')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.content == b'ok')

    @override_settings(SIMPLE_HEALTH_CHECKS={'simple_health_check.checks.dummy.DummyFalse': None})
    def test_no_readiness(self):
        apps.get_app_config('simple_health_check').register_checks()

        response = self.client.get('/readiness/')
        self.assertTrue(response.status_code == 500)
        self.assertTrue(response.content == b'down')

    @override_settings(
        CACHES={
            'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
        },
        SIMPLE_HEALTH_CHECKS={'simple_health_check.checks.caches.CacheBackends': None},
    )
    def test_caches(self):
        apps.get_app_config('simple_health_check').register_checks()

        response = self.client.get('/readiness/')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.content == b'ok')

    @override_settings(
        CACHES={
            'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
            'c2': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
        },
        SIMPLE_HEALTH_CHECKS={
            'simple_health_check.checks.caches.CacheBackends': [
                dict(alias='default'),
                dict(alias='c2'),
            ],
        },
    )
    def test_cache_aliases(self):
        apps.get_app_config('simple_health_check').register_checks()

        response = self.client.get('/readiness/')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.content == b'ok')

    @override_settings(
        CACHES={
            'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
        },
        SIMPLE_HEALTH_CHECKS={
            'simple_health_check.checks.caches.CacheBackends': [
                dict(alias='default'),
                dict(alias='c2'),
            ],
        },
    )
    def test_cache_no_rediness(self):
        apps.get_app_config('simple_health_check').register_checks()

        response = self.client.get('/readiness/')
        self.assertTrue(response.status_code == 500)
        self.assertTrue(response.content == b'down')
