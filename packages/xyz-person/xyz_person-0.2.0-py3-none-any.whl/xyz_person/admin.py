from django.contrib import admin
from . import models

@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'city', 'create_time')
    search_fields = ('name', 'mobile', 'email')
    raw_id_fields = ('user',)

