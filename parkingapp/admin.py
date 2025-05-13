from django.contrib import admin
from parkingapp.models import Employee, EmployeeCar, Company, CarType, OutsiderCar, ParkingSlot, ParkingRecord

# Register your models here.

admin.site.register(Employee)
admin.site.register(EmployeeCar)
admin.site.register(Company)
admin.site.register(CarType)
admin.site.register(OutsiderCar)
admin.site.register(ParkingSlot)
admin.site.register(ParkingRecord)