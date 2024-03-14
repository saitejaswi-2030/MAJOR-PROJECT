from django.contrib import admin

from patient.models import *

# Register your models here.
admin.site.register(Patient)
admin.site.register(forgot_pwd_patient)
