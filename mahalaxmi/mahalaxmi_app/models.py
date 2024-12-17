from idlelib.pyparse import trans

from django.db import models
from django.utils.timezone import now

# Create your models here.

class Login(models.Model):
    username = models.CharField(max_length=100,null=True)
    password = models.CharField(max_length=100, null=True)
    utype = models.CharField(max_length=100,null=True)
    name= models.CharField(max_length=100, null=True)

class Register(models.Model):
    name = models.CharField(max_length=200, null=True)
    phone = models.IntegerField(null=True)
    address = models.CharField(max_length=500, null=True)
    email = models.CharField(max_length=200, null=True)
    password = models.CharField(max_length=200, null=True)

class Customer(models.Model):
    name = models.CharField(max_length=100)
    aadharNo = models.CharField(max_length=12)
    panNo = models.CharField(max_length=10)
    aadharAddress = models.CharField(max_length=255)
    presentAddress = models.CharField(max_length=255)
    phoneNo = models.CharField(max_length=15)
    altphoneNo = models.CharField(max_length=15, blank=True, null=True)
    jamenName = models.CharField(max_length=100)
    jamenAddress = models.CharField(max_length=255)
    jamenNo = models.CharField(max_length=20)
    loanAmt = models.DecimalField(max_digits=10, decimal_places=2)
    serialNo = models.IntegerField(unique=True)
    agreementNo = models.CharField(max_length=500,null=True)
    loanDate = models.DateField()
    loanpayDate = models.IntegerField(null=True)
    loanEnddate = models.DateField()
    loanDayCount = models.IntegerField(null=True)
    loanType = models.CharField(max_length=50)
    active = models.BooleanField(default=False)
    interestAmt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    objectValue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    jamenaadharNo = models.CharField(max_length=20, default='Pending')
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    customerImage = models.ImageField(upload_to='customers/', blank=True, null=True)
    jamenImage = models.ImageField(upload_to='jamen/', null=True, blank=True)
    date = models.DateField(null=True)
    aadharPdf = models.FileField(upload_to='pdfs/', blank=True, null=True)


class Company(models.Model):
    name =models.CharField(max_length=500, null=True)
    address = models.CharField(max_length=500, null=True)
    phoneNo = models.CharField(max_length=20,null=True)
    phoneNo1 = models.CharField(max_length=20,null=True)

class Users(models.Model):
    name =models.CharField(max_length=500, null=True)
    address = models.CharField(max_length=500, null=True)
    phoneNo = models.CharField(max_length=20,null=True)
    email = models.CharField(max_length=20,null=True)
    password = models.CharField(max_length=20, null=True)

class DailyLoan(models.Model):
    date = models.DateField(null=True)
    serialNo = models.CharField(max_length=200, null=True)
    amount = models.FloatField(null=True)
    balance = models.FloatField(null=True)
    loanType = models.CharField(max_length=100,null=True)



class LoanEntry(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    serialNo = models.CharField(max_length=100,null=True)
    date = models.DateField()
    loanType = models.CharField(max_length=100)
    loanAmt = models.DecimalField(max_digits=10, decimal_places=2)
    interestAmt = models.DecimalField(max_digits=10, decimal_places=2)
    enteredAmt = models.FloatField(null=True)
    principal = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2,null=True)



    def __str__(self):
        return f"Loan Entry for {self.customer.serialNo} on {self.date}"

class Loan(models.Model):
    serialNo = models.CharField(max_length=100,null=True)
    loan_id = models.CharField(max_length=20, unique=True, editable=False,null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True)
    loanAmt = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    loanDate = models.DateField(default=now,null=True)
    loanEnddate = models.DateField(null=True)
    loanType = models.CharField(max_length=50,null=True)
    loanDayCount = models.IntegerField(null=True, blank=True)
    loanpayDate = models.IntegerField(null=True, blank=True)
    interestAmt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    objectValue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to="loan_images/", null=True, blank=True)
    active = models.BooleanField(default=True)
    date = models.DateField(null=True)
    status = models.CharField(max_length=20, default='Pending')



    def save(self, *args, **kwargs):
        # Autogenerate loan_id on save if not already set
        if not self.loan_id:
            self.loan_id = f"LN{str(self.customer.id).zfill(5)}-{str(Loan.objects.count() + 1).zfill(4)}"
        super().save(*args, **kwargs)