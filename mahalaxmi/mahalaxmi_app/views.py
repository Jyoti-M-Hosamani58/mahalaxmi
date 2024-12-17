from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datetime_safe import date
from mahalaxmi_app.models import Login, Company, Users,Customer, LoanEntry, Loan
# Create your views here.
from django.core.files.storage import FileSystemStorage
import os
from mahalaxmi.settings import BASE_DIR
from django.db.models import Count, Q


from django.db.models import Q

from datetime import datetime
from django.db.models import Q

def admin_home(request):
    print("admin_home view is being called!")  # Debugging point

    # Count of employees in the Users table
    employee_count = Users.objects.count()

    # Count of customers in the Customer table
    customer_count = Customer.objects.count()
    completed_customer_count = Loan.objects.filter(status='Completed').count()

    # Define loan types to track
    loan_types = ['Daily Loan', 'Gold Loan', 'Vehicle Loan', 'Property Loan', 'Monthly Loan']

    # Prepare a dictionary to hold the count of each loan type
    loan_dict = {}

    # Count Daily Loans separately from the DailyLoan table
    loan_dict['Daily Loan'] = DailyLoan.objects.filter(
        serialNo__isnull=False  # Ensure serialNo matches a customer
    ).values('serialNo').distinct().count()

    print(f"Count for Daily Loan: {loan_dict['Daily Loan']}")  # Debugging point

    # Loop through the other loan types (excluding 'Daily Loan') and count matching entries in LoanEntry table
    for loan_type in loan_types[1:]:  # Skip 'Daily Loan'
        loan_count = LoanEntry.objects.filter(
            loanType=loan_type,
            customer__serialNo__isnull=False  # Ensure serialNo is not null in LoanEntry
        ).values('customer__serialNo').distinct().count()

        # Store the count for this loan type
        loan_dict[loan_type] = loan_count

        print(f"Count for {loan_type}: {loan_count}")  # Debugging point
    # Initialize the counter for missing loan entries
    missing_loan_count = 0
    missing_loan_customers = []

    # Get all loans that are active and have status "Pending", excluding 'Daily Loan'
    loans = Loan.objects.filter(
        customer__status='Pending',  # Only check loans for customers with status 'Pending'
    ).exclude(loanType='Daily Loan')  # Exclude 'Daily Loan' loans

    # Get the current date
    current_date = datetime.today().date()

    # Iterate over each loan to check if the loan has missing entries for the 10th day of each month
    for loan in loans:
        loan_date = loan.loanDate  # Get the loan start date
        loan_pay_date = loan.loanpayDate  # The 10th day for the loan pay date
        customer = loan.customer  # Get the associated customer
        status = loan.status  # Get the loan status
        missing_months = []  # Store missing months for this loan

        # Debug: Print the loan details
        print(f"Processing loan: {loan.loan_id} (Loan Date: {loan_date}, Status: {status})")

        # Loop through each month from the loan's start date until the current date
        while loan_date <= current_date and status != "Completed":
            # Skip current month if the loan pay date (10th) hasn't passed yet
            if loan_date.month == current_date.month and current_date.day < loan_pay_date:
                break  # Skip current month until the 10th passes

            # Check if there is a loan entry for the 10th day of the month
            if loan_date.month <= current_date.month:  # Ensure we're not looking into future months
                # First, check if there is a loan entry on the 10th day
                loan_entry_exists_on_10th = LoanEntry.objects.filter(
                    customer=customer,
                    date__year=loan_date.year,
                    date__month=loan_date.month,
                    date__day=loan_pay_date  # Ensure the loan entry is for the 10th day
                ).exists()

                # If no loan entry exists on the 10th, check if there's any loan entry for that month
                loan_entry_exists_after_10th = LoanEntry.objects.filter(
                    customer=customer,
                    date__year=loan_date.year,
                    date__month=loan_date.month,
                    date__day__gt=loan_pay_date  # Check for entries after the 10th
                ).exists()

                # If no entry exists on the 10th and there are no entries after the 10th, mark the month as missing
                if not loan_entry_exists_on_10th and not loan_entry_exists_after_10th:
                    missing_months.append(loan_date.strftime('%Y-%m-%d'))  # Store the missing month

            # Move to the next month
            next_month = loan_date.month + 1
            next_year = loan_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            loan_date = loan_date.replace(year=next_year, month=next_month)

            # Re-check the loan status after each month
            status = loan.status

        # If there are missing months, increment the counter and add the customer to the list
        if missing_months:
            missing_loan_count += 1
            missing_loan_customers.append({
                'customer': customer,
                'missing_months': missing_months
            })

    # Debug: Print the count of missing loan entries
    print(f"Missing Loan Entries Count: {missing_loan_count}")

    # Now, let's calculate how many customers have missing Daily Loan entries
    missing_daily_loan_count = 0  # Track how many customers have missing Daily Loan entries
    missing_daily_loan_customers = []  # List to track customers with missing Daily Loan entries

    # Filter customers who have status not 'Completed'
    customers = Loan.objects.filter(
        loanType='Daily Loan'
    ).exclude(status='Completed')
    print(f"Processing {customers.count()} customers.")

    for customer in customers:
        # Check if a DailyLoan entry exists for the customer with matching serialNo and current date
        daily_loan_exists = DailyLoan.objects.filter(
            serialNo=customer.serialNo,
            date=current_date
        ).exists()

        # If no DailyLoan entry exists for this customer and the loan type is 'Daily Loan'
        if not daily_loan_exists:
            missing_daily_loan_count += 1
            missing_daily_loan_customers.append({
                'customer': customer,
                'missing_on_date': current_date
            })

    # Debug: Print the count of missing Daily Loan entries
    print(f"Missing Daily Loan Entries Count: {missing_daily_loan_count}")

    # Debugging the final context
    context = {
        'employee_count': employee_count,
        'customer_count': customer_count,
        'completed_customer_count': completed_customer_count,  # Add completed customer count

        'daily_loan_count': loan_dict.get('Daily Loan', 0),
        'gold_loan_count': loan_dict.get('Gold Loan', 0),
        'vehicle_loan_count': loan_dict.get('Vehicle Loan', 0),
        'property_loan_count': loan_dict.get('Property Loan', 0),
        'monthly_loan_count': loan_dict.get('Monthly Loan', 0),
        'missing_loan_count': missing_loan_count,  # This is the total count of missing loans
        'missing_loan_customers': missing_loan_customers,  # List of customers with missing loans
        'missing_daily_loan_count': missing_daily_loan_count,  # This is the total count of missing Daily Loans
        'missing_daily_loan_customers': missing_daily_loan_customers
    }

    print("Context:", context)  # Debugging point

    return render(request, 'admin_home.html', context)


def get_missing_daily_loan_details():
    # Initialize list to store customers with missing Daily Loan records
    missing_daily_loan_customers = []
    current_date = datetime.today().date()

    # Filter customers whose status is not 'Completed'
    customers = Customer.objects.filter(~Q(status='Completed'))

    # Process each customer
    for customer in customers:
        # Check if a DailyLoan entry exists for the customer with matching serialNo and current date
        daily_loan_exists = DailyLoan.objects.filter(
            serialNo=customer.serialNo,
            date=current_date
        ).exists()

        # If no DailyLoan entry exists for this customer, add them to the list
        if not daily_loan_exists:
            missing_daily_loan_customers.append({
                'customer_id': customer.id,
                'name': customer.name,
                'serialNo': customer.serialNo,
                'loanType': customer.loanType,
                'loanDate': customer.loanDate,
                'status': customer.status,
                'loanAmt': customer.loanAmt,
                'loanpayDate': customer.loanpayDate,
                'loanEnddate': customer.loanEnddate,
                'loanDayCount': customer.loanDayCount,
                'interestAmt': customer.interestAmt,
                'objectValue': customer.objectValue,
                'jamenaadharNo': customer.jamenaadharNo,
                'aadharNo': customer.aadharNo,
                'phoneNo': customer.phoneNo,
                'altphoneNo': customer.altphoneNo,
                'presentAddress': customer.presentAddress,
                'aadharAddress': customer.aadharAddress,
                'date': customer.date,  # Assuming 'date' is important for display as well
                'missing_on_date': current_date  # Store the date the loan is missing
            })

    return missing_daily_loan_customers

from django.db.models import Q
from datetime import date
def customers_without_dailyloan_today_view(request):
    # Get today's date
    current_date = date.today()

    # Track the number of missing daily loan entries and the customers with missing entries
    missing_daily_loan_count = 0
    missing_daily_loan_customers = []

    # Filter customers who have status not 'Completed'
    customers = Customer.objects.filter(~Q(status='Completed'))

    print(f"Processing {customers.count()} customers.")

    # Loop through each customer to check if a DailyLoan entry exists for them on the current date
    for customer in customers:
        # Check if a DailyLoan entry exists for the customer with the current date
        daily_loan_exists = DailyLoan.objects.filter(
            serialNo=customer.serialNo,
            date=current_date
        ).exists()

        # If no DailyLoan entry exists for this customer
        if not daily_loan_exists:
            missing_daily_loan_count += 1  # Increment the count of missing daily loans

            # Fetch related loan details from the Loan table for customers with a status other than 'Completed'
            loan_details = Loan.objects.filter(
                customer=customer,
                loanType='Daily Loan'  # Only fetch loans where loanType is 'Daily Loan'
            ).exclude(status='Completed').first()  # Exclude completed loans

            # Add the customer and their loan details to the missing list if loan details exist
            if loan_details:
                missing_daily_loan_customers.append({
                    'customer': customer,  # Store the customer object
                    'missing_on_date': current_date,  # Track the missing entry date
                    'loan_type': loan_details.loanType,  # Get loan type
                    'loan_amount': loan_details.loanAmt,  # Get loan amount
                    'loan_status': loan_details.status,  # Get loan status
                })

    # Debug: Print the count of missing Daily Loan entries
    print(f"Missing Daily Loan Entries Count: {missing_daily_loan_count}")

    # Now you can pass missing_daily_loan_customers to the template for display
    return render(request, 'get_missing_daily_loan_details.html', {
        'missing_daily_loan_customers': missing_daily_loan_customers,
        'missing_daily_loan_count': missing_daily_loan_count,
        'current_date': current_date
    })


def user_home(request):
    return render(request,'user_home.html')

def userlogin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        request.session['username'] = username
        ucount = Login.objects.filter(username=username).count()
        if ucount >= 1:
            udata = Login.objects.get(username=username)
            upass = udata.password
            utype = udata.utype
            if password == upass:
                request.session['utype'] = utype
                if utype == 'user':
                    return render(request, 'user_home.html')
                if utype == 'admin':
                    return redirect('admin_home')
            else:
                return render(request, 'userlogin.html', {'msg': 'Invalid Password'})
        else:
            return render(request, 'userlogin.html', {'msg': 'Invalid Username'})
    return render(request, 'userlogin.html')


def company(request):
    # Assuming you want to handle only a single company, for instance, by company ID or a fixed company.
    company = Company.objects.first()  # Get the first company in the database or None

    if request.method == "POST":
        name = request.POST.get('company')
        phone = request.POST.get('phone')
        phone1 = request.POST.get('phone1')
        address = request.POST.get('address')

        if company:
            # If the company exists, update it
            company.name = name
            company.phoneNo = phone
            company.phoneNo1 = phone1
            company.address = address

            company.save()
        else:
            # If the company does not exist, create a new one
            Company.objects.create(
                name=name,
                phoneNo=phone,
                phoneNo1=phone1,
                address=address
            )

    return render(request, 'company.html', {'company': company})

def viewCompany(request):
    company = Company.objects.first()
    return render(request,'viewCompany.html',{'company': company})

def users(request):
    # Assuming you want to handle only a single company, for instance, by company ID or a fixed company.

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        address = request.POST.get('address')

        Users.objects.create(
                name=name,
                phoneNo=phone,
                email=email,
                password=password,
                address=address
            )
        Login.objects.create(
                username=phone,
                password=password,
                utype="user"
            )

    return render(request, 'user.html')

def viewUser(request):
    employees = Users.objects.all()  # Fetch all employee records
    return render(request, 'viewUsers.html', {'employees': employees})

def editUser(request, pk):
    return render(request,'editUser.html')

def deleteUser(request, pk):
    return render(request,'viewUsers.html')


import uuid
import os
from django.core.files.base import ContentFile
import base64
from datetime import datetime
import logging



from django.shortcuts import render, HttpResponse
from django.core.files.base import ContentFile
from decimal import Decimal
from datetime import datetime
import base64
import logging

from django.http import JsonResponse

def customer(request):
    if request.method == 'POST' and request.FILES.get('image'):
        now = datetime.now().replace(microsecond=0)
        con_date = now.strftime("%Y-%m-%d")

        # Generate new serial number
        try:
            last_customer = Customer.objects.latest('serialNo')
            new_serial_no = last_customer.serialNo + 1
        except Customer.DoesNotExist:
            new_serial_no = 1

        serial_no = request.POST.get('serialNo')
        if serial_no:
            try:
                serial_no = int(serial_no)
            except ValueError:
                logging.error("Invalid serial number provided.")
                return JsonResponse({"error": "Invalid serial number provided."}, status=400)
        else:
            serial_no = new_serial_no

        # Extract form data
        required_fields = ['name', 'aadharNo', 'phoneNo', 'loanAmt', 'loanDate', 'loanEnddate', 'loanType']
        for field in required_fields:
            if not request.POST.get(field):
                logging.error(f"Missing required field: {field}")
                return JsonResponse({"error": f"Missing required field: {field}"}, status=400)

        name = request.POST.get('name')
        aadhar_no = request.POST.get('aadharNo')
        phone_no = request.POST.get('phoneNo')
        loan_amt = request.POST.get('loanAmt')
        loan_date = request.POST.get('loanDate')
        loan_end_date = request.POST.get('loanEnddate')
        loan_type = request.POST.get('loanType')

        # Optional fields
        pan_no = request.POST.get('panNo')
        agreement = request.POST.get('agreement')
        aadhar_address = request.POST.get('aadharAddress')
        present_address = request.POST.get('presentAddress')
        alt_phone_no = request.POST.get('altphoneNo', '')
        jamen_name = request.POST.get('jamenName')
        jamen_address = request.POST.get('jamenAddress')
        jamen_no = request.POST.get('jamenNo')
        jamenaadhar_no = request.POST.get('jamenaadharNo')
        loan_day_count = request.POST.get('loanDayCount', None)
        loanpay_date = request.POST.get('loanpayDate')
        interest_amt = request.POST.get('interestAmt', None)
        object_value = request.POST.get('objectValue', None)
        image = request.FILES.get('image', None)
        active = 'active' in request.POST

        if request.method == 'POST' and request.FILES.get('pdf'):
            pdf_file = request.FILES['pdf']

            # Optional: Validate the file type (ensure it's a PDF)
            if not pdf_file.name.endswith('.pdf'):
                return JsonResponse({"error": "Invalid file type. Please upload a PDF."}, status=400)

            # Save the PDF file
            fs = FileSystemStorage()  # You can also specify a custom location here
            filename = fs.save(pdf_file.name, pdf_file)
            file_url = fs.url(filename)

        customer_image_data = request.POST.get("customerImage")
        customer_image_file = None

        if customer_image_data:
            try:
                existing_images_count = Customer.objects.exclude(customerImage="").count()
                next_image_number = existing_images_count + 1
                format, imgstr = customer_image_data.split(';base64,')
                ext = format.split('/')[-1]
                customer_image_file = ContentFile(
                    base64.b64decode(imgstr),
                    name=f"customer_image_{next_image_number}.{ext}"
                )
            except Exception as e:
                logging.error(f"Error decoding customer image: {e}")
                return JsonResponse({"error": "Invalid customer image data."}, status=400)

        jamen_image_data = request.POST.get("jamenImageData")
        jamen_image_file = None

        if jamen_image_data:
            try:
                existing_jamen_images_count = Customer.objects.exclude(customerImage="").count()
                next_jamen_image_number = existing_jamen_images_count + 1
                format, imgstr = jamen_image_data.split(';base64,')
                ext = format.split('/')[-1]
                jamen_image_file = ContentFile(
                    base64.b64decode(imgstr),
                    name=f"jamen_image_{next_jamen_image_number}.{ext}"
                )
            except Exception as e:
                logging.error(f"Error decoding jamen image: {e}")
                return JsonResponse({"error": "Invalid jamen image data."}, status=400)

        try:
            loan_amt = Decimal(loan_amt)
            interest_amt = Decimal(interest_amt) if interest_amt else None
            object_value = Decimal(object_value) if object_value else None
        except ValueError:
            logging.error("Invalid input data for numeric fields.")
            return JsonResponse({"error": "Invalid numeric data."}, status=400)

        # Save Customer
        customer_instance = Customer.objects.create(
            serialNo=serial_no,
            name=name,
            aadharNo=aadhar_no,
            panNo=pan_no,
            agreementNo=agreement,
            aadharAddress=aadhar_address,
            presentAddress=present_address,
            phoneNo=phone_no,
            altphoneNo=alt_phone_no,
            jamenName=jamen_name,
            jamenAddress=jamen_address,
            jamenNo=jamen_no,
            jamenaadharNo=jamenaadhar_no,
            active=active,
            customerImage=customer_image_file,
            jamenImage=jamen_image_file,
            aadharPdf=pdf_file,
        )

        Loan.objects.create(
            customer=customer_instance,
            loanAmt=loan_amt,
            loanDate=loan_date,
            loanEnddate=loan_end_date,
            loanType=loan_type,
            loanDayCount=loan_day_count if loan_day_count else None,
            loanpayDate=loanpay_date if loanpay_date else None,
            interestAmt=interest_amt,
            objectValue=object_value,
            image=image,
            active=active,
            serialNo=serial_no,
            date=con_date,
            status='Pending',
        )

        try:
            # Save the customer and loan data...
            return JsonResponse({'message': "Customer data saved successfully!"}, status=201)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
    else:
        serial_numbers = Customer.objects.order_by('serialNo').values_list('serialNo', flat=True)
        serial_numbers = [sn for sn in serial_numbers if sn is not None]

        if serial_numbers:
            full_range = set(range(1, max(serial_numbers) + 1))
            existing_serials = set(serial_numbers)
            missing_serials = sorted(full_range - existing_serials)
        else:
            missing_serials = []

        return render(request, 'customer.html', {'missing_serials': missing_serials})



def viewCustomer(request):
    # Get the search query from the request (if any)
    search_query = request.GET.get('search', '')

    # If there is a search query, filter customers by serialNo or name
    if search_query:
        customers = Customer.objects.filter(
            serialNo__icontains=search_query
        ) | Customer.objects.filter(
            name__icontains=search_query
        )
    else:
        # If no search query, return all customers
        customers = Customer.objects.all()

    # Pass the customers and search query to the template
    return render(request, 'customerList.html', {'customers': customers, 'search_query': search_query})



def editCustomer(request, customer_id):
    # Fetch the existing customer from the database
    customer = get_object_or_404(Customer, id=customer_id)

    # Handle POST request (form submission)
    if request.method == 'POST':
        # Extract data from the POST request
        name = request.POST.get('name')
        aadharNo = request.POST.get('aadharNo')
        panNo = request.POST.get('panNo')
        aadharAddress = request.POST.get('aadharAddress')
        presentAddress = request.POST.get('presentAddress')
        phoneNo = request.POST.get('phoneNo')
        altphoneNo = request.POST.get('altphoneNo')
        jamenName = request.POST.get('jamenName')
        jamenAddress = request.POST.get('jamenAddress')
        jamenNo = request.POST.get('jamenNo')
        jamenaadharNo = request.POST.get('jamenaadharNo')




        # Update customer data
        customer.name = name
        customer.aadharNo = aadharNo
        customer.panNo = panNo
        customer.aadharAddress = aadharAddress
        customer.presentAddress = presentAddress
        customer.phoneNo = phoneNo
        customer.altphoneNo = altphoneNo
        customer.jamenName = jamenName
        customer.jamenAddress = jamenAddress
        customer.jamenNo = jamenNo
        customer.jamenaadharNo = jamenaadharNo



        # Save the updated customer data to the database
        customer.save()

        # Redirect to a confirmation page or the customer detail page
        return redirect('viewCustomer')  # Replace with your actual redirect target

    # Handle GET request (render form with existing customer data)
    return render(request, 'editCustomer.html', {'customer': customer})


def deleteCustomer(request, customer_id):
    # Fetch the customer to delete
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    return redirect('viewCustomer')


def deleteLoan(request, serialNo):
    # Check if serialNo exists in LoanEntry table
    loan_entries = LoanEntry.objects.filter(customer__serialNo=serialNo)

    if loan_entries.exists():  # If serialNo exists in LoanEntry
        loan_entries.delete()  # Delete all matching records from LoanEntry

    # Check if serialNo exists in DailyLoan table
    daily_loans = DailyLoan.objects.filter(serialNo=serialNo)

    if daily_loans.exists():  # If serialNo exists in DailyLoan
        daily_loans.delete()  # Delete all matching records from DailyLoan

    # Redirect to the 'viewCustomer' page or any other page after deletion
    return redirect('viewCustomer')

from django.http import JsonResponse
from .models import DailyLoan
from datetime import datetime, timedelta

from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum

from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone


def dailyLoanEntry(request):
    if request.method == 'POST':
        serialNo = request.POST.get('serialNo')
        date = request.POST.get('date')  # Get date from frontend
        amount = request.POST.get('amount')

        # Convert amount to Decimal if provided, else default to 0.00
        if amount:
            amount = Decimal(amount)  # Convert amount to Decimal
        else:
            amount = Decimal('0.00')  # Set to 0 if no amount is provided

        # Convert 'date' to a datetime object (with time set to midnight)
        date = datetime.strptime(date, '%Y-%m-%d')
        date = datetime.combine(date, datetime.min.time())  # Make it a datetime object with midnight time

        # Make sure the 'date' is timezone-aware
        date = timezone.make_aware(date) if timezone.is_naive(date) else date

        # Fetch the customer based on serialNo (Customer model contains serialNo)
        try:
            customer = Customer.objects.get(serialNo=serialNo)
        except Customer.DoesNotExist:
            error_message = f"Error: No customer found with serial number {serialNo}."
            return render(request, 'dailyLoanEntry.html', {'error_message': error_message})

        # Now, find the corresponding Loan for this customer
        try:
            loan = Loan.objects.get(customer=customer, loanType="Daily Loan")
        except Loan.DoesNotExist:
            error_message = f"Error: No loan of type 'Daily Loan' found for customer with serial number {serialNo}."
            return render(request, 'dailyLoanEntry.html', {'error_message': error_message})

        # Get the last record date for this serialNo
        last_record = DailyLoan.objects.filter(serialNo=serialNo).order_by('-date').first()

        if last_record:
            # If a last record exists, get its balance and convert it to Decimal
            last_balance = Decimal(last_record.balance) if isinstance(last_record.balance,
                                                                      float) else last_record.balance
        else:
            # If no record exists, start balance at loanAmt (initial loan amount)
            last_balance = Decimal(loan.loanAmt)  # Using loanAmt from Loan object as Decimal

        # Handle missing dates if there is a gap between the last record and the new date
        if last_record and date.date() > last_record.date:
            missing_dates = []
            temp_date = last_record.date + timedelta(days=1)  # Start from the day after the last record
            while temp_date < date.date():
                missing_dates.append(temp_date)
                temp_date += timedelta(days=1)

            # Insert records for the missing dates with amount as None (null) and balance from the last record
            for missing_date in missing_dates:
                if not DailyLoan.objects.filter(serialNo=serialNo, date=missing_date).exists():
                    DailyLoan.objects.create(
                        serialNo=serialNo,
                        date=missing_date,
                        amount=None,
                        balance=last_balance,  # Carry forward the last balance
                        loanType='Daily Loan'
                    )
                    last_balance = last_balance  # No change in balance for missing dates

        # Now, for the new entry, calculate balance from the last balance
        balance = last_balance - amount  # Both are now Decimal, no type mismatch

        # Create the new record if it does not exist already
        if not DailyLoan.objects.filter(serialNo=serialNo, date=date.date()).exists():
            DailyLoan.objects.create(
                serialNo=serialNo,
                date=date.date(),  # Store as date (no time)
                amount=amount,
                balance=balance,  # Save the balance calculated from the previous record
                loanType='Daily Loan'
            )

        # Check if the balance is zero after this entry
        if balance == Decimal('0.00'):
            # If balance is zero, update the Customer's status to 'Completed'
            customer.status = 'Completed'
            customer.save()  # Save the customer status

        # Optionally, you can get the count of records for the given serialNo in the DailyLoan table
        loan_count = DailyLoan.objects.filter(serialNo=serialNo).count()

        # Return a response (you could also redirect or show success message)
        return render(request, 'dailyLoanEntry.html', {'loan_count': loan_count})

    # If the method is not POST, simply render the page
    return render(request, 'dailyLoanEntry.html')


def get_loan_tabledata(request):
    selected_date = request.GET.get('date')  # Get the selected date from the request

    if selected_date:
        # Filter records by the selected date
        loans = DailyLoan.objects.filter(date=selected_date).values('serialNo', 'date', 'amount', 'balance')

        # List to store loan data
        loan_list = []

        # Get the total count of loans for the selected date

        for loan in loans:
            try:
                # Fetch the customer record based on serialNo
                customer = Loan.objects.get(serialNo=loan['serialNo'], loanType='Daily Loan')
                daycount1 = customer.loanDayCount  # Get the daycount from the Customer model
            except Customer.DoesNotExist:
                daycount1 = 0  # If no customer found, set daycount1 to 0 (or handle as needed)

            serial_no_count = DailyLoan.objects.filter(serialNo=loan['serialNo']).count()

            # Add the loan information to the loan_list, using the total loan count
            loan_list.append({
                'serialNo': loan['serialNo'],
                'date': loan['date'].strftime('%Y-%m-%d'),  # Format the date
                'amount': loan['amount'],
                'balance': loan['balance'],
                'daycount1': daycount1,  # Add the daycount from Customer
                'daycount': serial_no_count,  # Set the same total loan count for all entries
            })

        return JsonResponse({'loans': loan_list})
    else:
        return JsonResponse({'loans': []})  # If no date is provided, return an empty response


import json  # Import the json module
from django.utils.dateparse import parse_date

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt  # Allow POST requests without CSRF token for AJAX (be cautious)
def update_loan(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Parse the JSON body
        serial_no = data.get('serialNo')
        date = parse_date(data.get('date'))
        amount = data.get('amount')
        balance = data.get('balance')

        try:
            # Find the loan record by serial number and date
            loan = DailyLoan.objects.get(serialNo=serial_no, date=date)
            # Update the loan record
            loan.amount = amount
            loan.balance = balance
            loan.save()

            return JsonResponse({'success': True})

        except DailyLoan.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Loan record not found'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


# API endpoint to get previous date and amount based on serialNo
def get_loan_data(request, serialNo):
    loan = DailyLoan.objects.filter(serialNo=serialNo).order_by('-date').first()
    if loan:
        return JsonResponse({
            'previous_date': loan.date.strftime('%Y-%m-%d'),
            'amount': loan.amount
        })
    else:
        return JsonResponse({
            'previous_date': None,
            'amount': None
        })

from decimal import Decimal

from django.contrib import messages




def loanEntry(request):
    customers = Loan.objects.exclude(loanType='Daily Loan')  # Get customers whose loanType is not 'Daily Loan'
    loan_entries = LoanEntry.objects.all()  # Fetch all loan entries for display

    if request.method == 'POST':
        # Handle form submission manually
        serial_no = request.POST.get('serialName')
        entered_amt = request.POST.get('enteredAmt')
        principal = request.POST.get('principal')
        date = request.POST.get('date')

        try:
            # Get the customer loan object, excluding 'Daily Loan' loanType
            customer_loan = Loan.objects.filter(serialNo=serial_no).exclude(loanType='Daily Loan').first()

            if not customer_loan:
                # If no loan found (other than 'Daily Loan'), show an error message
                messages.error(request, "Error: No loan found for this customer (excluding 'Daily Loan').")
                return redirect('loanEntry')  # Redirect back to the loanEntry page

            # Get the actual Customer instance
            customer = Customer.objects.get(serialNo=serial_no)

        except Loan.DoesNotExist:
            messages.error(request, "Customer with the specified loan not found.")
            return redirect('loanEntry')  # Redirect back if customer does not exist
        except Customer.DoesNotExist:
            messages.error(request, "Customer not found.")
            return redirect('loanEntry')  # Redirect back if customer does not exist

        # Ensure entered amount and principal are treated as Decimals
        try:
            if entered_amt:
                entered_amt = Decimal(entered_amt)  # Convert entered amount to Decimal for consistency
            else:
                entered_amt = Decimal(0)  # If no entered amount, default to 0

            if principal:
                principal = Decimal(principal)  # Convert principal to Decimal for proper validation and storage
            else:
                principal = Decimal(0)  # Default to 0 if principal is not provided
        except (ValueError, TypeError) as e:
            messages.error(request, f"Invalid input: {str(e)}. Please check entered amount and principal.")
            return redirect('loanEntry')  # Redirect if invalid data is entered

        # Check if there are existing loan entries for the customer (based on serialNo)
        existing_entries = LoanEntry.objects.filter(serialNo=serial_no).order_by('-date')

        # Calculate the new balance
        if existing_entries.exists():
            last_entry = existing_entries.first()  # Most recent entry (first in descending order)
            last_balance = last_entry.balance  # Last balance from the most recent loan entry

            # Convert last_balance to Decimal if it's a float (to ensure compatibility)
            last_balance = Decimal(last_balance)

            # Calculate new balance
            new_balance = last_balance - principal
        else:
            # If no previous entries, use the customer’s loanAmt as the starting balance
            new_balance = Decimal(customer_loan.loanAmt) - principal  # Ensure loanAmt is a Decimal

        # Ensure new_balance is not negative (optional business rule)
        if new_balance < 0:
            messages.error(request, "Error: The loan entry exceeds available balance.")
            return redirect('loanEntry')

        # Create a new LoanEntry and save it
        loan_entry = LoanEntry(
            customer=customer,  # Use the actual Customer instance here
            serialNo=serial_no,
            date=date or timezone.now().date(),  # Use the current date if no date provided
            loanType=customer_loan.loanType,
            loanAmt=customer_loan.loanAmt,
            interestAmt=customer_loan.interestAmt,
            enteredAmt=entered_amt,
            principal=principal,
            balance=new_balance,  # Use the calculated new balance
        )
        loan_entry.save()

        # Check if the balance is zero after this entry
        if new_balance == 0:
            # If balance is zero, update the Customer's status to 'Completed'
            customer_loan.status = 'Completed'
            customer_loan.save()  # Save the customer status

        # Optionally, you could also show a success message
        messages.success(request, "Loan entry successfully created!")

        return redirect('loanEntry')  # Redirect to reload the page

    return render(request, 'loanEntry.html', {
        'customers': customers,
        'loan_entries': loan_entries,
    })


def get_customer_details_list(request, serial_no):
    # Filter by serialNo and loanType="Gold Loan" and get all matching entries
    loans = Loan.objects.filter(serialNo=serial_no).exclude(loanType="Daily Loan")

    if loans.exists():
        # Assuming you want to return the first loan for simplicity
        loan = loans.first()

        # Prepare the data for the single loan
        data = {
            'serialNo': loan.serialNo,
            'loanType': loan.loanType,
            'loanAmt': str(loan.loanAmt),
            'interestAmt': str(loan.interestAmt),
        }
        return JsonResponse(data)
    else:
        # Return an error if no matching loans are found
        return JsonResponse({'error': 'Gold Loan not found for this serialNo'}, status=404)


def loanHistory(request, customer_id):
    # Check if customer_id exists in LoanEntry table
    loan_entries = LoanEntry.objects.filter(customer__serialNo=customer_id)

    # Check if customer_id exists in DailyLoan table
    daily_loans = DailyLoan.objects.filter(serialNo=customer_id)

    # Get customer details from the Customer model
    customer = Customer.objects.filter(serialNo=customer_id).first()

    # Determine which table has data for the given customer_id
    if loan_entries.exists():
        loan_data = loan_entries
        loan_source = "LoanEntry"
    elif daily_loans.exists():
        loan_data = daily_loans
        loan_source = "DailyLoan"
    else:
        loan_data = None
        loan_source = "None"

    # Pass the data and source information to the template
    return render(request, 'loanHistory.html', {
        'loan_data': loan_data,
        'loan_source': loan_source,
        'customer': customer  # Passing customer data to template
    })
def daily_loan_count_page(request):
    # Filter the Loan table by loanType 'Daily Loan' and prefetch related Customer data
    daily_loan_customers = Loan.objects.filter(loanType='Daily Loan').select_related('customer')

    # Pass the filtered loans with customer details to the template
    return render(request, 'daily_loan_count_page.html', {'daily_loan_customers': daily_loan_customers})

def gold_loan_count_page(request):
    gold_loan_customers = Loan.objects.filter(loanType='Gold Loan').select_related('customer')
    return render(request, 'gold_loan_count_page.html', {'gold_loan_customers': gold_loan_customers})

def vehicle_loan_count_page(request):
    daily_loan_customers = Loan.objects.filter(loanType='Vehicle Loan').select_related('customer')

    return render(request, 'vehicle_loan_count_page.html', {'daily_loan_customers': daily_loan_customers})

def monthly_loan_count_page(request):
    daily_loan_customers = Loan.objects.filter(loanType='Monthly Loan').select_related('customer')

    return render(request, 'monthly_loan_count_page.html', {'daily_loan_customers': daily_loan_customers})

def property_loan_count_page(request):
    daily_loan_customers = Loan.objects.filter(loanType='Property Loan').select_related('customer')

    return render(request, 'property_loan_count_page.html', {'daily_loan_customers': daily_loan_customers})


from datetime import datetime


def loan_pending_count_page(request):
    # Filter out loans with 'Daily Loan' type
    loans = Loan.objects.exclude(loanType='Daily Loan')

    result = []  # Store the result for each customer
    current_date = datetime.today().date()  # Get the current date

    for loan in loans:
        customer = loan.customer  # Get the related customer for this loan
        loan_date = loan.loanDate  # Start date for loan

        # Check if loan_date is None
        if loan_date is None:
            continue  # Skip this loan if loanDate is None

        loan_pay_date = loan.loanpayDate  # The pay date to check every month (e.g., 10)
        status = loan.status  # Check loan status

        missing_months = []  # To store the missing months for this loan

        # Loop through the months starting from loanDate until status is "Completed"
        while loan_date <= current_date and status != "Completed":
            # Skip checking for the current month if the 10th hasn't passed yet
            if loan_date.month == current_date.month and loan_pay_date is not None and current_date.day < loan_pay_date:
                break  # Skip the current month until the loan_pay_date passes

            # Check for loan entry for the current month
            if loan_date.month <= current_date.month:  # Ensure the loan_date is not in the future
                loan_entry_before_or_on_pay_date = LoanEntry.objects.filter(
                    customer=customer,
                    date__year=loan_date.year,
                    date__month=loan_date.month,
                    date__day__lte=loan_pay_date if loan_pay_date is not None else 31
                    # Ensure that if loan_pay_date is None, we use a valid default (31st)
                ).exists()

                # If there's no loan entry on or before the loan pay date, add the month to missing_months list
                if not loan_entry_before_or_on_pay_date:
                    missing_months.append(loan_date.strftime('%Y-%m-%d'))

                # Check if there are any loan entries for the current month after the loan pay date
                if loan_pay_date is not None:  # Check only if loan_pay_date is valid
                    loan_entry_after_pay_date = LoanEntry.objects.filter(
                        customer=customer,
                        date__year=loan_date.year,
                        date__month=loan_date.month,
                        date__day__gt=loan_pay_date  # Loan entry after the loan pay date (e.g., after the 10th)
                    ).exists()

                    # If there is any loan entry after the loan pay date, we should NOT add this month as missing
                    if loan_entry_after_pay_date:
                        missing_months = [month for month in missing_months if month != loan_date.strftime('%Y-%m-%d')]

            # Move to the next month (manually adjust year and month)
            next_month = loan_date.month + 1
            next_year = loan_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            # Set loan_date to the same day in the next month
            loan_date = loan_date.replace(year=next_year, month=next_month)

            # Re-check the status to see if the loan is completed
            status = loan.status

        # If there are missing months, add this loan and missing months to the result
        if missing_months:
            loan_details = {
                'loan_id': loan.loan_id,
                'loan_type': loan.loanType,
                'loan_amount': loan.loanAmt,
                'loan_date': loan.loanDate,
                'loan_end_date': loan.loanEnddate,
                'loan_pay_date': loan.loanpayDate  # Including loan pay date
            }

            result.append({
                'customer': customer,
                'missing_months': missing_months,
                'loan_details': loan_details  # Add the loan details to the result
            })

    # If no results found, return a message
    if not result:
        result = "No missing loan entries found for any customer."

    # Render the page with the filtered results
    return render(request, 'loan_pending_count_page.html', {'result': result})

def loan_completed(request):
    daily_loan_customers = Loan.objects.filter(status='Completed').select_related('customer')
    return render(request,'loan_completed.html',{'daily_loan_customers':daily_loan_customers})

def get_customer_name(request):
    query = request.GET.get('query', '')
    if query:
        customers = Customer.objects.filter(name__icontains=query).values('name', 'serialNo')
        # Convert to a list of dicts containing both 'name' and 'serialNo'
        customer_data = [{'name': customer['name'], 'serialNo': customer['serialNo']} for customer in customers]
        print('Fetched customers:', customer_data)  # Debugging: check the data
        return JsonResponse(customer_data, safe=False)
    return JsonResponse([], safe=False)

def get_customer_details(request):
    name = request.GET.get('name', '')
    if name:
        customer = Customer.objects.filter(name=name).first()
        if customer:
            data = {
                'name': customer.name,
                'serialNo': customer.serialNo,
            }
        else:
            data = {}
    else:
        data = {}

    return JsonResponse(data)


def index(request):
    return render(request,'index.html')


def recoveryReport(request):
    loan_history = None  # Default to None in case no data is found
    total_amount = 0  # Default total amount

    if request.method == 'POST':
        # Get the 'from' and 'to' date from the form submission
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        if from_date and to_date:
            # Convert from_date and to_date from string to date format
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            # Filter DailyLoan model based on the date range
            loan_history = DailyLoan.objects.filter(date__range=[from_date, to_date])

            # Calculate the total amount (e.g., total balance or amount)
            total_amount = loan_history.aggregate(Sum('amount'))['amount__sum'] or 0
            # If using LoanEntry model, you can filter like this:
            # loan_history = LoanEntry.objects.filter(date__range=[from_date, to_date])
            # And sum the 'loanAmt' field, for example:
            # total_amount = loan_history.aggregate(Sum('loanAmt'))['loanAmt__sum'] or 0

    # Render the template and pass the loan_history and total_amount to it
    return render(request, 'recoveryReport.html', {'loan_history': loan_history, 'total_amount': total_amount})

def loanRecoveryReport(request):
    loan_history = None  # Default to None in case no data is found
    total_amount = 0  # Default total amount
    total_amountprincipal = 0  # Default total amount

    if request.method == 'POST':
        # Get the 'from' and 'to' date from the form submission
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        if from_date and to_date:
            # Convert from_date and to_date from string to date format
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            # Filter DailyLoan model based on the date range
            loan_history = LoanEntry.objects.filter(date__range=[from_date, to_date])

            # Calculate the total amount (e.g., total balance or amount)
            total_amountprincipal = loan_history.aggregate(Sum('principal'))['principal__sum'] or 0
            total_amount = loan_history.aggregate(Sum('enteredAmt'))['enteredAmt__sum'] or 0
            # If using LoanEntry model, you can filter like this:
            # loan_history = LoanEntry.objects.filter(date__range=[from_date, to_date])
            # And sum the 'loanAmt' field, for example:
            # total_amount = loan_history.aggregate(Sum('loanAmt'))['loanAmt__sum'] or 0

    # Render the template and pass the loan_history and total_amount to it
    return render(request, 'loanRecoveryReport.html', {'loan_history': loan_history, 'total_amount': total_amount,'total_amountprincipal':total_amountprincipal})

from django.db.models import Sum


def outgoingReport(request):
    loan_history = None  # Default to None in case no data is found
    total_amount = 0  # Default total amount
    total_amountbalance = 0  # Default total amount

    if request.method == 'POST':
        # Get the 'from' and 'to' date from the form submission
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        if from_date and to_date:
            # Convert from_date and to_date from string to date format
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            # Filter Customer model based on the date range
            customer_records = Loan.objects.filter(date__range=[from_date, to_date])

            loan_history = []
            total_amount = 0

            # Iterate over the filtered customer records to determine the appropriate loan record
            for customer in customer_records:
                loan_type = customer.loanType
                serial_no = customer.serialNo
                name = customer.customer.name  # Assuming 'customer' is the ForeignKey to Customer
                customer_date = customer.date  # Get the date from the Customer model
                loan_amount = customer.loanAmt  # Get the loanAmt from the Customer model

                if loan_type == 'Daily Loan':
                    # Fetch the latest balance from the DailyLoan table
                    daily_loan_record = DailyLoan.objects.filter(serialNo=serial_no).order_by('-date').first()
                    if daily_loan_record:
                        balance = daily_loan_record.balance
                    else:
                        balance = loan_amount  # If no balance, use loanAmt as balance
                else:
                    # Fetch the latest balance from the LoanEntry table
                    loan_entry_record = LoanEntry.objects.filter(serialNo=serial_no).order_by('-date').first()
                    if loan_entry_record:
                        balance = loan_entry_record.balance
                    else:
                        balance = loan_amount  # If no balance, use loanAmt as balance

                # Add to the loan history
                loan_history.append({
                    'serialNo': serial_no,
                    'name': name,
                    'date': customer_date,  # Add the date from the Customer model
                    'loanType': loan_type,
                    'loanAmt': loan_amount,  # Add the loanAmt from the Customer model
                    'balance': balance,
                })

                total_amountbalance += float(balance)  # Update the total amount balance
                total_amount += float(loan_amount)  # Update the total amount

    # Render the template and pass the loan_history and total_amount to it
    return render(request, 'outgoingReport.html', {'loan_history': loan_history, 'total_amount': total_amount, 'total_amountbalance': total_amountbalance})


from django.http import HttpResponse
from decimal import Decimal

def add_customer(request):
    if request.method == 'POST':

        now = datetime.now().replace(microsecond=0)
        con_date = now.strftime("%Y-%m-%d")
        # Handling serial number logic
        try:
            last_loan = Customer.objects.latest('serialNo')
            new_serial_no = last_loan.serialNo + 1
        except Customer.DoesNotExist:
            new_serial_no = 1
        # Extract form data from POST request
        name = request.POST.get('name')
        aadhar_no = request.POST.get('aadharNo')
        pan_no = request.POST.get('panNo')
        aadhar_address = request.POST.get('aadharAddress')
        present_address = request.POST.get('presentAddress')
        phone_no = request.POST.get('phoneNo')
        alt_phone_no = request.POST.get('altphoneNo', '')  # Optional field

        jamen_name = request.POST.get('jamenName')
        jamen_address = request.POST.get('jamenAddress')
        jamen_no = request.POST.get('jamenNo')

        loan_amt = request.POST.get('loanAmt')
        loan_date = request.POST.get('loanDate')
        loan_end_date = request.POST.get('loanEnddate')
        loan_type = request.POST.get('loanType')
        loan_day_count = request.POST.get('loanDayCount', None)  # Optional field
        active = 'active' in request.POST  # Checkbox value

        loanpay_date = request.POST.get('loanpayDate')  # Handling image upload (optional)
        interest_amt = request.POST.get('interestAmt', None)
        object_value = request.POST.get('objectValue', None)

        # Handle the file uploads (optional)
        image = request.FILES.get('image', None)  # This will be None if no image is uploaded
        jamenImage = request.FILES.get('jamenImage', None)  # Optional field for jamen image
        customerImage = request.FILES.get('customerImage', None)  # Optional field for jamen image

        # Convert loan_amt, interest_amt, and object_value to Decimal
        try:
            loan_amt = Decimal(loan_amt)
            interest_amt = Decimal(interest_amt) if interest_amt else None
            object_value = Decimal(object_value) if object_value else None
        except ValueError:
            return HttpResponse("Invalid input data for numeric fields", status=400)

        # Validate required fields
        if not name or not aadhar_no or not pan_no or not aadhar_address or not present_address or not phone_no:
            return HttpResponse("Missing required fields", status=400)

        # Create and save the Customer object
        customer = Customer(
            name=name,
            aadharNo=aadhar_no,
            panNo=pan_no,
            aadharAddress=aadhar_address,
            presentAddress=present_address,
            phoneNo=phone_no,
            altphoneNo=alt_phone_no,
            jamenName=jamen_name,
            jamenAddress=jamen_address,
            jamenNo=jamen_no,
            loanAmt=loan_amt,
            loanDate=loan_date,
            loanEnddate=loan_end_date,
            loanType=loan_type,
            loanDayCount=loan_day_count,
            active=active,
            loanpayDate=loanpay_date,
            interestAmt=interest_amt,
            objectValue=object_value,
            status='Pending',
            image=image,
            jamenImage=jamenImage,  # Optional Jamen Image
            customerImage=customerImage,
            date=con_date,
            serialNo=new_serial_no
        )

        # Save the customer instance
        customer.save()

        return redirect('add_customer')  # Redirect to success page after saving

    return render(request, 'CustomerEntry.html')  # Render form on GET request


def loanPrincipleRecoveryReport(request):
    loan_history = None  # Default to None in case no data is found
    total_amount = 0  # Default total amount
    total_amountprincipal = 0  # Default total amount

    if request.method == 'POST':
        # Get the 'from' and 'to' date from the form submission
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        if from_date and to_date:
            # Convert from_date and to_date from string to date format
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            # Filter DailyLoan model based on the date range
            loan_history = LoanEntry.objects.filter(date__range=[from_date, to_date],principal__gt=0)

            # Calculate the total amount (e.g., total balance or amount)
            total_amountprincipal = loan_history.aggregate(Sum('principal'))['principal__sum'] or 0
            total_amount = loan_history.aggregate(Sum('enteredAmt'))['enteredAmt__sum'] or 0
            # If using LoanEntry model, you can filter like this:
            # loan_history = LoanEntry.objects.filter(date__range=[from_date, to_date])
            # And sum the 'loanAmt' field, for example:
            # total_amount = loan_history.aggregate(Sum('loanAmt'))['loanAmt__sum'] or 0

    # Render the template and pass the loan_history and total_amount to it
    return render(request, 'loanPrincipleRecoveryReport.html', {'loan_history': loan_history, 'total_amount': total_amount,'total_amountprincipal':total_amountprincipal})

def add_loan(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    serial_no = customer.serialNo

    if request.method == 'POST':

        now = datetime.now().replace(microsecond=0)
        con_date = now.strftime("%Y-%m-%d")


        # Get form data
        loanAmt = request.POST.get('loanAmt')
        loanDate = request.POST.get('loanDate')
        loanEnddate = request.POST.get('loanEnddate')
        loanType = request.POST.get('loanType')
        loanDayCount = request.POST.get('loanDayCount', None)
        loanpayDate = request.POST.get('loanpayDate', None)
        interestAmt = request.POST.get('interestAmt', None)
        objectValue = request.POST.get('objectValue', None)
        image = request.FILES.get('image', None)
        active = request.POST.get('active') == 'True'

        # Save to Loan model
        loan = Loan.objects.create(
            customer=customer,
            loanAmt=loanAmt,
            loanDate=loanDate,
            loanEnddate=loanEnddate,
            loanType=loanType,
            loanDayCount=loanDayCount if loanDayCount else None,
            loanpayDate=loanpayDate if loanpayDate else None,
            interestAmt=interestAmt if interestAmt else None,
            objectValue=objectValue if objectValue else None,
            image=image,
            active=active,
            serialNo=serial_no,
            date=con_date,
            status='Pending',

        )

        return redirect('add_loan', customer_id=customer.id)

    # Fetch loan history for the customer
    loans = Loan.objects.filter(customer=customer)

    return render(request, 'add_loan.html', {
        'customer': customer,
        'loans': loans,
    })
