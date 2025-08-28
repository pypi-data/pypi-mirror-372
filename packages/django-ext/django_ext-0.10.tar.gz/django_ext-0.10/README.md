Django Ext
==========

Some extensions for Django.

# Models

## TimestampModel

Add `created_at` and `updated_at` for model.

## TimeRangeModel

Add `started_at` and `ended_at` for model.

## UserTrackModel

Add `created_by` and `update_by` for model.

This model requires `django-currentuser`, and should add it to the middleware classes in your settings.py:

```
MIDDLEWARE = (
    ...,
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
)
```

## ExtraFieldsManager

`ExtraFieldsManager` is intended to be used in conjunction with `ExtraFieldsQuerySet` to filter extra added fields using custom filter conditions.

While initializing the `ExtraFieldsManager` class, it is necessary to use the `fields` parameter to specify extra fields and their corresponding filter conditions generation functions.

Usage:

```
class MyModel(models.Model):
    relation = models.ForeignKey(RelationModel, models.CASCADE, +, null=False)

    objects = ExtraFieldsManager(fields={
        # users: an extra field that is not present in the model
        # lambda function: used to generate complex query conditions
        'users': lambda x: Q(relation__data__users__contained_by=[str(user.id) for user in x]) | \
        Q(relation__data__groups__contained_by=Group.objects.filter(user__in=x).distinct().values_list('id', flat=True))
    })
```

# Commands

## translate

Translate the permission names into the local language.

```
$ python manage.py translate
```