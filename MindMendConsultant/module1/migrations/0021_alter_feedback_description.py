# Generated by Django 5.0 on 2024-01-15 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module1', '0020_remove_customerreport_assessment_observation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='description',
            field=models.TextField(default=''),
        ),
    ]