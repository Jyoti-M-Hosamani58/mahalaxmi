# Generated by Django 3.0 on 2024-12-16 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mahalaxmi_app', '0005_auto_20241216_0037'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='serialNo',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
