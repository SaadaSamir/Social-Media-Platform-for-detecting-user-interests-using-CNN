# Generated by Django 3.0.2 on 2023-05-02 18:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0013_interest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interest',
            name='post',
        ),
    ]
