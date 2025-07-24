from django.db import models

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)

class PublishedReviewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published') 