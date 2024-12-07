from django.db import models

# Create your models here.

class Interest_neuron(models.Model):
    username = models.TextField(max_length=140, blank=True)
    content = models.TextField(max_length=140, blank=True)