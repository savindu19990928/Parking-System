from django.contrib import admin
from .models import CarType, Company, ParkingSlot, Employee, OutsiderCar, ParkingRecord, Price
from django.urls import path
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import ParkingRecordSerializer
from .utils import generate_remote_report
import os
import math
from django.conf import settings

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
    
    change_form_template = "companyadmin.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:company_id>/download-parking-json/',
                self.admin_site.admin_view(self.download_parking_json),
                name='download_parking_json',
            ),
        ]
        return custom_urls + urls

    @method_decorator(csrf_exempt)
    def download_parking_json(self, request, company_id):
        company = Company.objects.get(pk=company_id)

        start_date = parse_date(request.GET.get("start_date", ""))
        end_date = parse_date(request.GET.get("end_date", ""))

        queryset = ParkingRecord.objects.filter(company=company, removed_at__isnull=False)
        if start_date:
            queryset = queryset.filter(parked_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(parked_at__date__lte=end_date)

        serializer = ParkingRecordSerializer(queryset, many=True)
        
        price = Price.objects.first()
        
        total_duration_seconds = sum(
            (record.removed_at - record.parked_at).total_seconds()
            for record in queryset
            if record.parked_at and record.removed_at
        )
        total_duration_hours = math.ceil(total_duration_seconds / 3600)
        
        parameters = {
            "Parameter1": company.name,
            "Parameter2": str(price.price),
            "Parameter3": str(total_duration_hours),
            "Parameter4": str(total_duration_hours*price.price)
        }
        
        root_dir = settings.BASE_DIR  
        jasper_path = os.path.join(root_dir, 'reports', 'Invoice.jasper')
        pdf_buffer = generate_remote_report("https://jasper-522049904205.europe-west1.run.app/report/pdf", jasper_path, serializer.data, parameters)
        return HttpResponse(pdf_buffer, content_type='application/pdf')

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
