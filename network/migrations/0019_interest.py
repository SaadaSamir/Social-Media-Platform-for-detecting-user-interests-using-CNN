# Generated by Django 3.0.2 on 2023-05-02 20:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0018_delete_interest'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_txt', models.TextField(blank=True, max_length=140)),
                ('count', models.IntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inter', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'content_txt')},
            },
        ),
    ]
