# Generated by Django 5.0 on 2024-01-03 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module1', '0009_remove_bookedsession_paypal_payment_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookedsession',
            name='date_time',
        ),
        migrations.AddField(
            model_name='bookedsession',
            name='payment_method',
            field=models.CharField(default='nayapay', max_length=50),
        ),
        migrations.AddField(
            model_name='therapist',
            name='earnings',
            field=models.DecimalField(decimal_places=2, default=1000.0, max_digits=10),
        ),
    ]
