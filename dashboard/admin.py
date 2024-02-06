from django.contrib import admin
from .models import Author
class AuthodAdmin(admin.ModelAdmin):
 list_display=['first_name','last_name','email_text']
admin.site.register(Author,AuthodAdmin)

