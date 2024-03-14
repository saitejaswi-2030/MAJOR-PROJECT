from django.contrib import admin

from donor.models import *

# Register your models here.
admin.site.register(Donor)
admin.site.register(BloodDonate)
admin.site.register(forgot_pwd_model)