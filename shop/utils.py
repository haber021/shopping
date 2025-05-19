from .models import Setting

def get_setting(key, default=None):
    """
    Get a setting value from the database.
    If the setting doesn't exist, return the default value.
    """
    try:
        setting = Setting.objects.get(key=key)
        return setting.value
    except Setting.DoesNotExist:
        return default

def set_setting(key, value):
    """
    Set a setting value in the database.
    If the setting already exists, update it.
    If not, create a new one.
    """
    setting, created = Setting.objects.update_or_create(
        key=key,
        defaults={'value': value}
    )
    return setting
