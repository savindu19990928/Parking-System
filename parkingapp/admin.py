from django.contrib import admin
from .models import CarType, Company, ParkingSlot, Employee, OutsiderCar, ParkingRecord, Price

admin.site.site_header = "Parking System"
admin.site.site_title = "Parking System"
admin.site.index_title = "Welcome to Parking System Admin Dashboard"

def get_fields_without_id(model, field_type_filter=None):
    fields = [f.name for f in model._meta.fields if f.name != 'id']
    if field_type_filter:
        fields = [f.name for f in model._meta.fields if f.name != 'id' and f.get_internal_type() in field_type_filter]
    return fields


@admin.register(CarType)
class CarTypeAdmin(admin.ModelAdmin):
    list_display = get_fields_without_id(CarType)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = get_fields_without_id(Company)
    search_fields = get_fields_without_id(Company, ['CharField'])


@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    list_display = get_fields_without_id(ParkingSlot)
    search_fields = get_fields_without_id(ParkingSlot, ['CharField'])
    list_filter = get_fields_without_id(ParkingSlot)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = get_fields_without_id(Employee)
    search_fields = get_fields_without_id(Employee, ['CharField'])
    list_filter = get_fields_without_id(Employee)


@admin.register(OutsiderCar)
class OutsiderCarAdmin(admin.ModelAdmin):
    list_display = get_fields_without_id(OutsiderCar)
    search_fields = get_fields_without_id(OutsiderCar, ['CharField'])


@admin.register(ParkingRecord)
class ParkingRecordAdmin(admin.ModelAdmin):
    list_display = get_fields_without_id(ParkingRecord)
    search_fields = get_fields_without_id(ParkingRecord, ['CharField'])
    list_filter = get_fields_without_id(ParkingRecord)

admin.site.register(Price)
