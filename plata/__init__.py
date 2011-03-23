VERSION = (0, 0, 1)
__version__ = '.'.join(map(str, VERSION))


import logging
logger = logging.getLogger('plata')


class LazySettings(object):
    def _load_settings(self):
        from plata import default_settings
        from django.conf import settings as django_settings

        for key in dir(default_settings):
            if not key.startswith('PLATA_'):
                continue

            setattr(self, key, getattr(django_settings, key,
                getattr(default_settings, key)))

    def __getattr__(self, attr):
        self._load_settings()
        del self.__class__.__getattr__
        return self.__dict__[attr]

settings = LazySettings()


_shop_instance = None
def register(instance):
    logger.debug('Registering shop instance: %s' % instance)

    global _shop_instance
    _shop_instance = instance

def shop_instance():
    # Load default URL patterns to ensure that the shop
    # object has been created
    from django.core.urlresolvers import get_resolver
    get_resolver(None)._populate()

    return _shop_instance
