from django.db import models
from django.forms import ValidationError

class CarType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=75)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")

    def __str__(self):
        return f"{self.name} ({self.company.name})"

class ParkingSlot(models.Model):
    id = models.AutoField(primary_key=True)
    slot_number = models.CharField(max_length=10, unique=True)
    owner = models.OneToOneField(
        'Employee',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='dedicated_slot'
    )

    def __str__(self):
        if self.owner:
            return f"Slot {self.slot_number} (Owner: {self.owner.name})"
        return f"Slot {self.slot_number}"

class EmployeeCar(models.Model):
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="cars")

    def __str__(self):
        return f"{self.employee.name if self.employee else 'Unassigned'}"


class OutsiderCar(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Outsider car ({self.car_type.name if self.car_type else 'Other'})"


class ParkingRecord(models.Model):
    id = models.AutoField(primary_key=True)
    parking_slot = models.ForeignKey(ParkingSlot, on_delete=models.SET_NULL, null=True)
    car_type = models.ForeignKey(CarType, on_delete=models.SET_NULL, null=True, blank=True)
    employee_car = models.ForeignKey(EmployeeCar, on_delete=models.SET_NULL, null=True, blank=True)
    outsider_car = models.ForeignKey(OutsiderCar, on_delete=models.SET_NULL, null=True, blank=True)
    parked_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)
    
    @property
    def is_occupied(self):
        return self.parkingrecord_set.filter(removed_at__isnull=True).exists()
    
    def clean(self):
        if not self.employee_car and not self.outsider_car:
            raise ValidationError("Either employee_car or outsider_car must be specified.")

    def __str__(self):
        if self.employee_car:
            return f"Employee Car: in {self.parking_slot}"
        elif self.outsider_car:
            return f"Outsider Car ({self.outsider_car.car_type}) in Slot {self.parking_slot}"
        return "Unknown parking record"