from django.contrib import admin
from .models import Software, SoftwareCategory, Article, News, Tag, Metier
from django.db import models
from tinymce.widgets import TinyMCE
from django import forms
from django.utils.html import format_html

class SoftwareInline(admin.TabularInline):
    model = Software.category.through
    extra = 1

class ArticleInline(admin.TabularInline):
    model = Article.category.through
    extra = 1


class SoftwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_display', 'is_top_pick', 'is_published')
    list_filter = ('category', 'is_top_pick', 'is_published')
    search_fields = ('name', 'description')
    filter_horizontal = ('category',)
    list_editable = ('is_top_pick', 'is_published')

    def category_display(self, obj):
        return ", ".join([category.name for category in obj.category.all()])
    category_display.short_description = 'Categories'

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'software_count', 'metier')
    search_fields = ('name', 'description')
    list_editable = ('metier',)
    inlines = [SoftwareInline, ArticleInline]

    def software_count(self, obj):
        return obj.categories_softwares_link.count()
    software_count.short_description = 'Number of Software'

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'is_published')
    search_fields = ('title', 'content')
    list_filter = ('category', 'is_published')

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_published', 'tag_list')
    list_filter = ('is_published', 'date', 'tags')
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

    def colored_tag(self, obj):
        return format_html('<span style="background-color: {}; color: {}; padding: 3px; border-radius: 5px;">{}</span>', obj.color, '#000000' if obj.color == '#FFFFFF' else '#FFFFFF', obj.name)
    colored_tag.short_description = 'Tag'

class MetierAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')

admin.site.register(Software, SoftwareAdmin)
admin.site.register(SoftwareCategory, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Metier, MetierAdmin)
