
import uuid
from django.db import models
from dashboard.models import Author
from dashboard.models import User

# tags model
class Tag(models.Model):

    name  = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name 
    
class Idea(models.Model):
    status = (
        ('active','active'),
        ('pending','pending')
    )

    title  = models.CharField(max_length=200, null=True)
    detail = models.TextField(max_length=2000, null=True)
    image = models.ImageField(upload_to='images/media', null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=20, choices=status, default='pending')
    #show_hide = models.CharField(max_length=5,choices=visibility, default='show')
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    featured  = models.BooleanField(default=False)
    visit_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Idea'

    def overview(self):
        short = self.detail[:30]
        return short 
    
    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url 

    def __str__(self):
        author_username = self.author.author.username if self.author and self.author.author else self.author.first_name
        return f"{self.title} | {author_username} | {self.status}"