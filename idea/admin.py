from django.contrib import admin
from .models import *
    

class CatAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

admin.site.register(Idea)
admin.site.register(IdeaFile)


# made by Nazrul Islam Yeasin 
# Facebook : https://facebook.com/yeazin.io
# Twitter : https://twitter.com/_yeazin
# Github : https://github.com/yeazin
# linked In : https://www.linkedin.com/in/yeazin/
# website : yeazin.github.io
