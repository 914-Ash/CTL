from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    author = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name='Email')
    email_text = models.CharField(max_length=255, blank=True, null=True, verbose_name='Email') 
    first_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='First Name')
    last_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Last Name')
    designation = models.CharField(max_length=10, null=True)
    author_image = models.ImageField(upload_to='author/', verbose_name='Author Profile Image', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Author'
    
    def __str__(self):
        if self.author:
            return self.author.username
        else:
            return "削除されたユーザ"

class SomeModel(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)