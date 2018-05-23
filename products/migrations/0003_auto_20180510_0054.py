# Generated by Django 2.0.4 on 2018-05-09 21:54

import django.core.files.storage
from django.db import migrations, models
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_productfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='productfile',
            name='auth_required',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productfile',
            name='free',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='productfile',
            name='file',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location='C:\\Users\\newprofile\\Documents\\DJANGO\\ecommerce\\static_cdn\\protected_media'), upload_to=products.models.upload_file_loc, verbose_name=products.models.Product),
        ),
    ]