from django.contrib import admin
from .models import Software, SoftwareCategory, Article, Actualites, Tag, Metier
from django.db import models
from tinymce.widgets import TinyMCE
from django import forms
from django.utils.html import format_html

class ActualitesInline(admin.TabularInline):
    model = Actualites.tags.through
    extra = 1
    ordering = ('tag__name',)

class ArticleInline(admin.TabularInline):
    model = Article.tags.through
    extra = 1
    ordering = ('tag__name',)

class SoftwareInline(admin.TabularInline):
    model = Software.category.through
    extra = 1
    ordering = ('softwarecategory__name',)


class SoftwareAdmin(admin.ModelAdmin):
    list_display = ['name', 'categories_list', 'metier', 'is_top_pick', 'is_published']
    fields = ['name', 'slug', 'description', 'excerpt', 'category', 'logo', 
              'is_published', 'image_principale', 'site', 'video', 'is_top_pick', 
              'unique_views', 'metier']
    list_filter = ('is_published',)
    list_editable = ['is_top_pick', 'metier']


    def formatted_description(self, obj):
        return format_html(obj.description)
    formatted_description.short_description = 'Description'

    def categories_list(self, obj):
        return ", ".join([category.name for category in obj.category.all()])
    categories_list.short_description = 'Catégories'

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_published', 'icon', 'software_count')
    search_fields = ('name', 'description')
    list_editable = ('slug', 'is_published', 'icon')
    inlines = [SoftwareInline]

    def software_count(self, obj):
        return Software.objects.filter(category=obj).count()
    software_count.short_description = 'Nombre de logiciels'

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'is_published')
    search_fields = ('title', 'content')
    list_filter = ('tags', 'is_published')

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

class ActualitesAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'is_published', 'tag_list')
    list_filter = ('is_published', 'pub_date', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)

    def tag_list(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    tag_list.short_description = 'Tags'

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

class TagAdminForm(forms.ModelForm):
    color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))

    class Meta:
        model = Tag
        fields = ['name', 'color']

class TagAdmin(admin.ModelAdmin):
    form = TagAdminForm
    list_display = ('name', 'color', 'colored_tag')
    search_fields = ('name',)
    inlines = [ActualitesInline, ArticleInline]


    def colored_tag(self, obj):
        return format_html('<span style="background-color: {}; color: {}; padding: 3px; border-radius: 5px;">{}</span>', obj.color, '#000000' if obj.color == '#FFFFFF' else '#FFFFFF', obj.name)
    colored_tag.short_description = 'Tag'

class MetierAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')

admin.site.register(Software, SoftwareAdmin)
admin.site.register(SoftwareCategory, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Actualites, ActualitesAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Metier, MetierAdmin)
