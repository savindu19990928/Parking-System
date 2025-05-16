from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import CarType, ParkingRecord, Price, Company, Employee, OutsiderCar
from django.utils.timezone import now
from math import ceil
from django.core.exceptions import ValidationError
from django.db import transaction

# Create your views here.

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Please provide both username and password."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"},
                            status=status.HTTP_401_UNAUTHORIZED)

class ParkingRecordCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        employee_id = request.data.get("employee_id")
        car_type_name = request.data.get("car_type_name")
        company_name = request.data.get("company_name")

        employee = None
        outsider_car = None
        company = None
        car_type = None
        has_dedicated_slot = False
        slot_number = None

        # Case 1: Employee car
        if employee_id:
            try:
                employee = Employee.objects.select_related('company', 'dedicated_slot').get(id=employee_id)
                company = employee.company
            except Employee.DoesNotExist:
                return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

            if ParkingRecord.objects.filter(employee_car=employee, removed_at__isnull=True).exists():
                return Response({"error": "Employee car is already parked."}, status=status.HTTP_400_BAD_REQUEST)

            if employee.dedicated_slot:
                has_dedicated_slot = True
                slot_number = employee.dedicated_slot.slot_number

        # Case 2: Outsider car
        elif car_type_name and not company_name:
            try:
                car_type = CarType.objects.get(name=car_type_name)
            except CarType.DoesNotExist:
                return Response({"error": "Invalid car_type_name."}, status=status.HTTP_404_NOT_FOUND)

            outsider_car = OutsiderCar.objects.create(car_type=car_type)

        # Case 3: Visitor/company car (not employee or outsider)
        elif company_name and car_type_name:
            try:
                company = Company.objects.get(name=company_name)
                car_type = CarType.objects.get(name=car_type_name)
            except (Company.DoesNotExist, CarType.DoesNotExist):
                return Response({"error": "Invalid company_name or car_type_name."}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response(
                {"error": "Provide a valid combination: employee_id, or car_type_name, or company_name + car_type_name"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check company slot limit
        if company and company.slot_limit > 0:
            active = ParkingRecord.objects.filter(company=company, removed_at__isnull=True).count()
            if active >= company.slot_limit:
                return Response(
                    {"error": f"All {company.slot_limit} slots for {company.name} are occupied."},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Create parking record
        try:
            car_type_value = car_type
            if not car_type_value and outsider_car:
                car_type_value = outsider_car.car_type

            company_value = company
            if not company_value:
                if employee and employee.company:
                    company_value = employee.company
                elif outsider_car and getattr(outsider_car, 'company', None):
                    company_value = outsider_car.company

            record = ParkingRecord.objects.create(
                employee_car=employee,
                outsider_car=outsider_car,
                car_type=None if employee else car_type_value,
                company=company_value
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "id": record.id,
            "date": now().date(),
            "parked_at": record.parked_at
        }

        if has_dedicated_slot:
            response_data["slot_number"] = slot_number

        return Response(response_data, status=status.HTTP_201_CREATED)

class ParkingSlotStatusView(APIView):
    permission_classes = [IsAuthenticated]  # Optional

    def get(self, request):
        company_name = request.query_params.get('company')
        company = Company.objects.get(name=company_name)
        
        available_slots = ParkingRecord.objects.filter(company=company, removed_at__isnull=True).count()
        
        
        if available_slots >= company.slot_limit:
            return Response({"error": f"All {company.slot_limit} slots for {company.name} are occupied."})
        else:
            return  Response(status=status.HTTP_200_OK)

class CarTypeNameListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        car_type_names = CarType.objects.values_list('name', flat=True)
        return Response(list(car_type_names), status=status.HTTP_200_OK)

class CompanyNameListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        company_names = Company.objects.values_list('name', flat=True)
        return Response(list(company_names), status=status.HTTP_200_OK)

class EmployeeNameListView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        try:
            company_name = request.query_params.get('company')
            company = Company.objects.get(name=company_name)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)

        employee_names = list(company.employees.all().values('id', 'name'))
        return Response(employee_names, status=status.HTTP_200_OK)

class RemoveCarAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        employee_car = request.data.get("employee_car", None)
        record_id = request.data.get("record_id", None)
        if employee_car:
            try:
                
                last_record = ParkingRecord.objects.filter(employee_car=employee_car).order_by('-parked_at').first()
                if not last_record:
                    return Response({"error": "No parking records found for this employee."}, status=status.HTTP_404_NOT_FOUND)
            except ParkingRecord.DoesNotExist:
                return Response({"error": "Parking record not found for the specified employee."}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                
                last_record = ParkingRecord.objects.get(id=record_id)
            except ParkingRecord.DoesNotExist:
                return Response({"error": "Parking record not found."}, status=status.HTTP_404_NOT_FOUND)

        if last_record.removed_at is not None:
            return Response({"error": "Car has already been removed."}, status=status.HTTP_400_BAD_REQUEST)

        current_time = now()
        today = current_time.date()

        last_record.removed_at = current_time
        last_record.save()

        duration = current_time - last_record.parked_at
        duration_minutes = duration.total_seconds() / 60
        duration_hours = duration.total_seconds() / 3600
        
        if last_record.employee_car is not None:
            response_data = {
                "parking_record_id": last_record.id,
                "parked_at": last_record.parked_at,
                "removed_at": last_record.removed_at,
                "today": str(today),
                "charged_units": 0,
                "unit": None,
                "price_per_unit": "0.00",
                "total_price": "0.00",
                "note": "Employee cars are free of charge."
            }
            
            if duration_hours >= 1:
                response_data["duration_hours"] = round(duration_hours, 2)
            else:
                response_data["duration_minutes"] = round(duration_minutes, 2)

            return Response(response_data, status=status.HTTP_200_OK)
        
        try:
            price_config = Price.objects.get()
        except Price.DoesNotExist:
            return Response({"error": "Pricing configuration not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if price_config.duration_unit == "Minutes":
            charged_units = ceil(duration_minutes)
            duration_field = {"duration_minutes": charged_units}
        elif price_config.duration_unit == "Hours":
            charged_units = ceil(duration_hours)
            duration_field = {"duration_hours": charged_units}
        else:
            return Response({"error": "Invalid duration unit in pricing configuration."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        total_price = charged_units * price_config.price

        response_data = {
            "parking_record_id": last_record.id,
            "parked_at": last_record.parked_at,
            "removed_at": last_record.removed_at,
            "today": str(today),
            "charged_units": charged_units,
            "unit": price_config.duration_unit,
            "price_per_unit": str(price_config.price),
            "total_price": str(total_price),
            **duration_field
        }

        return Response(response_data, status=status.HTTP_200_OK)