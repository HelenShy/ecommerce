# Generated by Django 2.0.5 on 2018-05-23 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_auto_20180520_0037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('paid', 'Paid'), ('created', 'Created')], default='created', max_length=60),
        ),
    ]
