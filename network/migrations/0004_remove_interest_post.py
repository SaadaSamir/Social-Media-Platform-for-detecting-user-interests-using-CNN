# Generated by Django 3.0.2 on 2023-05-02 14:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_interest_content_txt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interest',
            name='post',
        ),
    ]