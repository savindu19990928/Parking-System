from django.contrib import admin
from parkingapp.models import Employee, EmployeeCar, Company, CarType, OutsiderCar, ParkingSlot, ParkingRecord

admin.site.site_header = "Parking System"
admin.site.site_title = "Parking System"
admin.site.index_title = "Welcome to Parking System Admin Dashboard"

# Register your models here.

admin.site.register(Employee)
admin.site.register(EmployeeCar)
admin.site.register(Company)
admin.site.register(CarType)
admin.site.register(OutsiderCar)
admin.site.register(ParkingSlot)
admin.site.register(ParkingRecord)