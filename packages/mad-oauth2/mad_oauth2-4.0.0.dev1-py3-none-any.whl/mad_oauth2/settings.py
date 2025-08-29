from django.conf import settings
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured
from django.test.signals import setting_changed

USER_SETTINGS = getattr(settings, "MAD_OAUTH2", None)

DEFAULTS = {
    "THROTTLE_CLASS": "mad_oauth2.throttling.ThrottleClass"
}

IMPORT_STRINGS = (
    "THROTTLE_CLASS"
)

MANDATORY = IMPORT_STRINGS


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import %r for setting %r. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)



class MadOauth2Settings:

    def __init__(self, user_settings=None, defaults=None, import_strings=None, mandatory=None):
        self._user_settings = user_settings or {}
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self.mandatory = mandatory or ()
        self._cached_attrs = set()

    
    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "MAD_OAUTH2", {})
        return self._user_settings


    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid MAD_OAUTH2 setting: %s" % attr)
        
        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            val = self.defaults[attr]
        
        if val and attr in self.import_strings:
            val = perform_import(val, attr)
  
        self.validate_setting(attr, val)
        self._cached_attrs.add(attr)
        setattr(self, attr, val)    
        return val


    def validate_setting(self, attr, val):
        if not val and attr in self.mandatory:
            raise AttributeError("mad_oauth2 setting: %s is mandatory" % attr)
    
    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")

oauth2_settings = MadOauth2Settings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS, MANDATORY)


def reload_mad_oauth2_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "MAD_OAUTH2":
        oauth2_settings.reload()

setting_changed.connect(reload_mad_oauth2_settings)