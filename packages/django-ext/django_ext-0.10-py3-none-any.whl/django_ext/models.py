from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_currentuser.db.models import CurrentUserField


class TimestampModel(models.Model):
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        abstract = True


class TimeRangeModel(models.Model):
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    ended_at = models.DateTimeField(_('ended at'), null=True, blank=True)

    class Meta:
        abstract = True


class UserTrackModel(models.Model):
    created_by = CurrentUserField(on_delete=models.PROTECT, related_name='+', verbose_name=_('created by'))
    updated_by = CurrentUserField(on_delete=models.PROTECT, on_update=True, related_name='+', verbose_name=_('updated by'))

    class Meta:
        abstract = True


class ExtraFieldsQuerySet(models.QuerySet):
    def q(self, obj, key, value):
        for index, child in enumerate(obj.children):
            if isinstance(child, Q):
                self.q(child, key, value)
            else:
                if isinstance(child, tuple) and child[0] == key:
                    obj.children[index] = value(child[1])

    def _filter_or_exclude_inplace(self, negate, args, kwargs):
        for k, v in self.model.objects.fields.items():
            for index, arg in enumerate(args):
                if isinstance(arg, Q):
                    self.q(arg, k, v)
            if k in kwargs:
                self._query.add_q(v(kwargs.pop(k, None)))

        super(ExtraFieldsQuerySet, self)._filter_or_exclude_inplace(negate, args, kwargs)


class ExtraFieldsManager(models.Manager):
    def __init__(self, **kwargs):
        self.fields = kwargs.get('fields', {})
        super().__init__()

    def get_queryset(self):
        return ExtraFieldsQuerySet(self.model, using=self._db)
