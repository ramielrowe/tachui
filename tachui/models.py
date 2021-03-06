from django.contrib import admin
from django.db import models


class Deployment(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=300)
    is_default = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

admin.site.register(Deployment)