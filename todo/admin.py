from django.contrib import admin

from .models import Note, Group


admin.site.register(Note)
admin.site.register(Group)