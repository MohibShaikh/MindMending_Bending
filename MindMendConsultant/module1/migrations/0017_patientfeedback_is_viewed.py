# Generated by Django 5.0 on 2024-01-09 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module1', '0016_alter_patientfeedback_answer1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientfeedback',
            name='is_viewed',
            field=models.BooleanField(default=False),
        ),
    ]