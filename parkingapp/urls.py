from django.urls import path
from .views import (
    LoginAPIView,
    CarTypeNameListAPIView,
    ParkingRecordCreateAPIView,
    RemoveCarAPIView,
    CompanyNameListAPIView,
    EmployeeNameListView,
    ParkingSlotStatusView
)

urlpatterns = [
    # Auth
    path('login/', LoginAPIView.as_view(), name='api-login'),
    
    # Get car types
    path('cartypes/', CarTypeNameListAPIView.as_view(), name='car-type-names'),
    
    # Enter car
    path('enter/', ParkingRecordCreateAPIView.as_view(), name='enter-car'),
    
    # Remove car
    path('remove/', RemoveCarAPIView.as_view(), name='remove-car'),
    
    # Company list
    path('companylist/', CompanyNameListAPIView.as_view(), name='company-names'),
    
    # Employee list
    path('companies/', EmployeeNameListView.as_view(), name='employee-names'),
    
    # Company status
    path('status/', ParkingSlotStatusView.as_view(), name='status'),
]