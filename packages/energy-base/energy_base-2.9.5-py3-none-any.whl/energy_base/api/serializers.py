from energy_base.translation import translate as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class DashboardDateSerializer(serializers.Serializer):
    datetime = serializers.DateTimeField()
    period = serializers.ChoiceField(choices=['daily', 'hourly'], default='daily')


class DashboardSerializer(serializers.Serializer):
    datetime = serializers.DateTimeField(required=False)
    period = serializers.ChoiceField(choices=['hourly', 'today', 'daily', 'monthly', 'yearly'], default='daily')

    def validate(self, attrs):
        period = attrs.get('period', 'daily')
        datetime = attrs.get('datetime')

        if period != 'today' and datetime is None:
            raise ValidationError({
                'datetime': _('This field is required when period is not "today".')
            })
        return attrs
