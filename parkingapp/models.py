from django.db import models
from django.forms import ValidationError
from django.utils.timezone import now


class CarType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=15)

    class Meta:
        verbose_name = "Vehicle type"
        verbose_name_plural = "Vehicle types"

    def __str__(self):
        return self.name


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    slot_limit = models.PositiveIntegerField(
        default=0,
        help_text="Maximum number of active parking slots allowed for this company.",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=75)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")
    car_type = models.ForeignKey('CarType', on_delete=models.SET_NULL, null=True, blank=True)

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


class OutsiderCar(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    car_type = models.ForeignKey('CarType', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Outsider car ({self.car_type.name if self.car_type else 'Other'})"


class Price(models.Model):
    DURATION_CHOICES = [
        ("Hours", "Hours"),
        ("Minutes", "Minutes"),
    ]

    id = models.AutoField(primary_key=True)
    duration_unit = models.CharField(max_length=10, choices=DURATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if Price.objects.exists() and not self.pk:
            raise ValidationError("Only one Price entry is allowed.")

    def __str__(self):
        return f"{self.duration_unit} - {self.price}"


class ParkingRecord(models.Model):
    id = models.AutoField(primary_key=True)
    car_type = models.ForeignKey(CarType, on_delete=models.SET_NULL, null=True, blank=True)
    employee_car = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    outsider_car = models.ForeignKey(OutsiderCar, on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)
    parked_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        if self.employee_car:
            return f"Employee Car ({self.employee_car})"
        elif self.outsider_car:
            return f"Outsider Car ({self.outsider_car})"
        return "Unknown parking record"
