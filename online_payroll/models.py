from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from core_payroll.models import AuditModel


class Department(AuditModel):
    """
    Department model for organizing employees
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class PayHead(AuditModel):
    """
    Pay head model for defining earnings and deductions
    """
    TYPE_CHOICES = (
        ('earning', 'Earning'),
        ('deduction', 'Deduction'),
    )
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Employee(AuditModel):
    """
    Employee model with personal and employment details
    """
    TYPE_CHOICES = (
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('seasonal', 'Seasonal'),
    )
    
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees')
    employment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    join_date = models.DateField()
    base_salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    pay_heads = models.ManyToManyField(PayHead, through='EmployeePayHead')
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.employee_id})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def masked_bank_account(self):
        if not self.bank_account or len(self.bank_account) < 4:
            return ""
        return "****" + self.bank_account[-4:]


class EmployeePayHead(AuditModel):
    """
    Junction model between Employee and PayHead with amount
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    pay_head = models.ForeignKey(PayHead, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    class Meta:
        unique_together = ('employee', 'pay_head')

    def __str__(self):
        return f"{self.employee} - {self.pay_head}: {self.amount}"


class Payroll(AuditModel):
    """
    Payroll model for tracking payroll runs
    """
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.CharField(max_length=100)
    processed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Payroll {self.start_date} to {self.end_date}"


class SalarySlip(AuditModel):
    """
    Salary slip model for individual employee payments
    """
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='salary_slips')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_slips')
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Salary slip for {self.employee} - {self.payroll}"


class SalarySlipDetail(AuditModel):
    """
    Salary slip detail model for individual pay head amounts
    """
    TYPE_CHOICES = (
        ('earning', 'Earning'),
        ('deduction', 'Deduction'),
    )
    
    salary_slip = models.ForeignKey(SalarySlip, on_delete=models.CASCADE, related_name='details')
    pay_head_name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.pay_head_name}: {self.amount}"
