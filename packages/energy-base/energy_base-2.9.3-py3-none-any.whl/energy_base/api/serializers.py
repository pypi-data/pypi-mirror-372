from rest_framework import serializers


class DashboardDateSerializer(serializers.Serializer):
    datetime = serializers.DateTimeField()
    period = serializers.ChoiceField(choices=['daily', 'hourly'], default='daily')


class DashboardSerializer(serializers.Serializer):
    datetime = serializers.DateTimeField()
    period = serializers.ChoiceField(choices=['hourly', 'today', 'daily', 'monthly', 'yearly'], default='daily')
