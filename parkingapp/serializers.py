from rest_framework import serializers
from .models import ParkingRecord, CarType, Employee, OutsiderCar, Company


class CarTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarType
        fields = ['id', 'name']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name']


class EmployeeSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    car_type = CarTypeSerializer()

    class Meta:
        model = Employee
        fields = ['id', 'name', 'company', 'car_type']


class OutsiderCarSerializer(serializers.ModelSerializer):
    car_type = CarTypeSerializer()
    company = CompanySerializer()

    class Meta:
        model = OutsiderCar
        fields = ['id', 'car_type', 'company']


class ParkingRecordSerializer(serializers.ModelSerializer):
    car_type = CarTypeSerializer()
    employee_car = EmployeeSerializer()
    outsider_car = OutsiderCarSerializer()
    company = CompanySerializer()

    class Meta:
        model = ParkingRecord
        fields = [
            'id',
            'car_type',
            'employee_car',
            'outsider_car',
            'company',
            'parked_at',
            'removed_at',
        ]
