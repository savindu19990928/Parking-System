from rest_framework import serializers
from .models import ParkingRecord, Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name']

class ParkingRecordSerializer(serializers.ModelSerializer):
    car_type_name = serializers.CharField(source='car_type.name', read_only=True)
    employee_car_name = serializers.CharField(source='employee_car.name', read_only=True)
    outsider_car_id = serializers.CharField(source='outsider_car.id', read_only=True)
    company = CompanySerializer()

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
        ]
