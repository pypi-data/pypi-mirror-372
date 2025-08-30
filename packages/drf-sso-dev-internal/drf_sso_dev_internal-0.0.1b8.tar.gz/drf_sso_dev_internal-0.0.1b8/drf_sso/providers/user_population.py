from django.contrib.auth import get_user_model
from drf_sso.settings import api_settings
from django.core.exceptions import ImproperlyConfigured

User = get_user_model()
def base_user_population(payload, name):
    try:
        populate_user_conf = api_settings.PROVIDERS[name]['populate_user_conf']
        (payload_lookup, db_lookup) = populate_user_conf['lookup_field']
        mappings = populate_user_conf['mappings']
    except KeyError:
        raise ImproperlyConfigured(f'Provider "{name}" is using default user population method but doesn\'t provide a valid configuration.')
    
    user = User.objects.get_or_create(**{db_lookup: payload[payload_lookup]})
    for payload_field, db_field in mappings.items():
        setattr(user, db_field, payload[payload_field])
    user.save()
    return user, {}