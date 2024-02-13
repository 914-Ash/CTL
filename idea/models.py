from django.db import models
from django.dispatch import receiver
import os
from dashboard.models import Author

class IdeaFile(models.Model):
    idea = models.ForeignKey('Idea', on_delete=models.CASCADE)
    file = models.FileField(upload_to='idea_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, idea, file):
        idea_file = cls(idea=idea, file=file)
        idea_file.save()
        return idea_file

@receiver(models.signals.post_delete, sender=IdeaFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):

    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

class Idea(models.Model):
    status = (
        ('商品化', '商品化'),
        ('保留', '保留')
    )

    title = models.CharField(max_length=200, null=True)
    detail = models.TextField(max_length=2000, null=True)
    image = models.ImageField(upload_to='images/media', null=True, blank=True)
    status = models.CharField(max_length=20, choices=status, default='保留')
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    email_text = models.CharField(max_length=255, blank=True, null=True, verbose_name='Email')
    featured = models.BooleanField(default=False)
    visit_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    files = models.ManyToManyField(IdeaFile, related_name='idea_files', blank=True)

    class Meta:
        verbose_name_plural = 'Ideas'

    def overview(self):
        short = self.detail[:30]
        return short

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    def delete(self, *args, **kwargs):
        # Delete associated files
        for idea_file in self.files.all():
            idea_file.delete()

        # Delete the post itself
        super().delete(*args, **kwargs)

    def __str__(self):
        author_username = self.author.author.username if self.author and self.author.author else self.author.first_name
        return f"{self.title} | {author_username} | {self.status}"
