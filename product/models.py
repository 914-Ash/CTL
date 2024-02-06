from django.db import models
from dashboard.models import Author

class Tag(models.Model):
    name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name 

class Product(models.Model):
    status = (
        ('active', 'active'),
        ('pending', 'pending')
    )

    title = models.CharField(max_length=200, null=True)
    description = models.TextField(max_length=2000, null=True)
    image = models.ImageField(upload_to='images/products', null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=20, choices=status, default='pending')
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Products'

    def overview(self):
        short = self.description[:30]
        return short 

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url 

    def __str__(self):
        return f"{self.title} | {self.author.author.username} | {self.status}"
