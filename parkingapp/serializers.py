from rest_framework import serializers
from .models import ParkingRecord, CarType, Employee, OutsiderCar, Company


class CarTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarType
        fields = ['name']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name']


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ['name']


class OutsiderCarSerializer(serializers.ModelSerializer):

    class Meta:
        model = OutsiderCar
        fields = ['id']


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
