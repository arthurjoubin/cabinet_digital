from django.db import models
from django.utils import timezone
from django.urls import reverse



class Article(models.Model):
    title = models.CharField(max_length=200)
    excerpt = models.TextField()
    content = models.TextField()
    pub_date = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='articles/images', null=True, blank=True)
    category = models.ManyToManyField('SoftwareCategory', related_name='articles')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})
    
class Software(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True,unique=False)
    description = models.TextField()
    category = models.ManyToManyField('SoftwareCategory', related_name='categories_softwares_link')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    editeur = models.CharField(max_length=100)
    image_principale = models.ImageField(upload_to='images/',null=True, blank=True)
    site = models.URLField(max_length=200, blank=True)
    video = models.URLField(max_length=200, blank=True)
    is_top_pick = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_top_pick', 'name']  # Order by top pick status, then name

    def __str__(self):
        return self.name



class SoftwareCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(blank=True,unique=False)


    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = "Software Categories"
