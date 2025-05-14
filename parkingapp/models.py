from django.db import models

class CarType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ParkingSlot(models.Model):
    id = models.AutoField(primary_key=True)
    slot_number = models.CharField(max_length=10)
    is_assigned = models.BooleanField(default=False)
    assigned_company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="parking_slots"
    )

    def __str__(self):
        return f"Slot {self.slot_number}"


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")
    dedicated_slot = models.CharField(max_length=5, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.company.name})"


class EmployeeCar(models.Model):
    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="cars")
    license_plate = models.CharField(max_length=20, unique=True)
    car_type = models.ForeignKey(CarType, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.license_plate} - {self.employee.name if self.employee else 'Unassigned'}"


class OutsiderCar(models.Model):
    id = models.AutoField(primary_key=True)
    car_type = models.ForeignKey(CarType, on_delete=models.SET_NULL, null=True)
    entry_time = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Outsider car ({self.car_type.name if self.car_type else 'Unknown'})"


class ParkingRecord(models.Model):
    id = models.AutoField(primary_key=True)
    parking_slot = models.ForeignKey(ParkingSlot, on_delete=models.SET_NULL, null=True, blank=True)
    employee_car = models.ForeignKey(EmployeeCar, on_delete=models.SET_NULL, null=True, blank=True)
    outsider_car = models.ForeignKey(OutsiderCar, on_delete=models.SET_NULL, null=True, blank=True)
    parked_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        if self.employee_car:
            return f"Employee Car: {self.employee_car.license_plate} in Slot {self.parking_slot}"
        elif self.outsider_car:
            return f"Outsider Car ({self.outsider_car.car_type}) in Slot {self.parking_slot}"
        return "Unknown parking record"