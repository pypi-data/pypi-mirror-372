from django.conf import settings
from django.utils.translation import gettext_lazy as _

USER_SETTINGS = getattr(settings, 'EXT', {})

DEFAULTS = {
    'ACTIONS': {'add': _('add'), 'change': _('change'), 'delete': _('delete'), 'view': _('view')}
}

globals().update({**DEFAULTS, **USER_SETTINGS})
