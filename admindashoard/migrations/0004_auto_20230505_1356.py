# Generated by Django 3.0.2 on 2023-05-05 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admindashoard', '0003_auto_20230505_1230'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interest_neuron',
            name='user',
        ),
        migrations.AddField(
            model_name='interest_neuron',
            name='username',
            field=models.TextField(blank=True, max_length=140),
        ),
    ]
