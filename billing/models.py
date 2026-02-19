from django.db import models
from decimal import Decimal
# Create your models here.
# billing/models.py
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from decimal import Decimal
from decimal import Decimal, ROUND_HALF_UP
import uuid

class Client(models.Model):
    name = models.CharField(max_length=200)
    mobile_1 = models.CharField(max_length=15)
    mobile_2 = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=30, blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # %

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name





class Project(models.Model):

    STATUS_CHOICES = (
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('hold', 'On Hold'),
    )

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    budget = models.DecimalField(max_digits=12, decimal_places=2)  # Contract Value
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_paid(self):
        return self.payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal("0.0")

    @property
    def total_spent(self):
        total = self.spends.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('area') * F('rate') * F('qty'),
                    output_field=DecimalField(max_digits=18, decimal_places=2)
                )
            )
        )['total'] or Decimal("0.00")

        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def yet_to_receive(self):
        return self.budget - self.total_paid

    @property
    def profit(self):
        return self.budget - self.total_spent

    def __str__(self):
        return f"{self.name} - {self.client.name}"



class FloorType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class RoomType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name




class FullSemi(models.Model):
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.rate}"




from decimal import Decimal

class Spend(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='spends')
    floor = models.ForeignKey(FloorType, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True, blank=True)
    fullsemi = models.ForeignKey(FullSemi, on_delete=models.SET_NULL, null=True, blank=True)

    # 🔥 NEW COLUMN
    elements = models.CharField(max_length=200, null=True, blank=True)

    description = models.TextField(blank=True, null=True)

    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    area = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    unit = models.CharField(max_length=50, default="sqft")

    rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    qty = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        # Calculate area
        if self.length is not None and self.width is not None:
            self.area = self.length * self.width
        else:
            self.area = None

        # Auto assign rate from FullSemi
        if self.fullsemi:
            self.rate = self.fullsemi.rate

        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        area = self.area or Decimal("0.00")
        rate = self.rate or Decimal("0.00")
        qty = self.qty or Decimal("0.00")

        if area > 0:
            total = area * rate * qty
        else:
            total = rate * qty

        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def __str__(self):
        type_name = self.fullsemi.name if self.fullsemi else "No Type"
        return f"{self.project.name} - {type_name}"



class Payment(models.Model):

    PAYMENT_MODES = (
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('bank', 'Bank Transfer'),
        ('cheque', 'Cheque'),
    )

    # ✅ ADD THESE
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES)

    invoice_token = models.UUIDField(
        editable=False,
        null=True,
        unique=True
    )

    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_token:
            self.invoice_token = uuid.uuid4()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project.name} - {self.amount}"
