from rest_framework import serializers
from .models import ParkingRecord, Company
from django.utils.dateformat import format as date_format
from django.utils.timezone import localtime


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name']


class ParkingRecordSerializer(serializers.ModelSerializer):
    car_type_name = serializers.CharField(source='car_type.name', read_only=True)
    employee_car_name = serializers.SerializerMethodField()
    outsider_car_id = serializers.CharField(source='outsider_car.id', read_only=True)
    company = CompanySerializer()
    parked_at = serializers.SerializerMethodField()
    removed_at = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()

    class Meta:
        model = ParkingRecord
        fields = [
            'id',
            'car_type_name',
            'employee_car_name',
            'outsider_car_id',
            'company',
            'parked_at',
            'removed_at',
            'duration_hours',
        ]

    def get_employee_car_name(self, obj):
        return obj.employee_car.name if obj.employee_car and obj.employee_car.name else " "

    def get_parked_at(self, obj):
        return date_format(localtime(obj.parked_at), 'M d, Y h:i A') if obj.parked_at else " "

    def get_removed_at(self, obj):
        return date_format(localtime(obj.removed_at), 'M d, Y h:i A') if obj.removed_at else " "

    def get_duration_hours(self, obj):
        if obj.parked_at and obj.removed_at:
            delta = obj.removed_at - obj.parked_at
            return round(delta.total_seconds() / 3600, 2)
        return " "

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        for key, value in rep.items():
            if value is None:
                rep[key] = " "
            elif isinstance(value, dict):
                rep[key] = {k: (" " if v is None else v) for k, v in value.items()}

        return rep
