# Generated by Django 3.1.4 on 2020-12-22 20:14

from django.db import migrations


def add_data(apps, schema_editor):
    Type = apps.get_model('main', 'EventType')
    Type.objects.create(name='wyklad')


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0005_auto_20210102_1745'),
    ]

    operations = [
        migrations.RunPython(add_data, reverse_code=migrations.RunPython.noop)
    ]
