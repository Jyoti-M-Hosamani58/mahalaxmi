# Generated by Django 3.0 on 2024-12-16 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mahalaxmi_app', '0007_loan_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='status',
            field=models.CharField(default='Pending', max_length=20),
        ),
    ]
