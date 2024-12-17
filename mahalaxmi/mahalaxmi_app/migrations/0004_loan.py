# Generated by Django 3.0 on 2024-12-15 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mahalaxmi_app', '0003_customer_agreementno'),
    ]

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serialNo', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=255)),
                ('loanId', models.CharField(max_length=100, unique=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('interest_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
            ],
        ),
    ]
