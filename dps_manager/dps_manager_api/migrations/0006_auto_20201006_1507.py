# Generated by Django 3.0.5 on 2020-10-06 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dps_manager_api', '0005_auto_20201006_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kpi',
            name='hidden',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='kpi',
            name='removed',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='parameter',
            name='hidden',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='parameter',
            name='removed',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]