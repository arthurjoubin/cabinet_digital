from django.contrib import admin
from .models import Software, SoftwareCategory, Article
from django.urls import path
from django.core.management import call_command
from django.http import HttpResponseRedirect



class SoftwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_display', 'editeur', 'is_top_pick')
    list_filter = ('category', 'editeur', 'is_top_pick')
    search_fields = ('name', 'editeur')
    filter_horizontal = ('category',)
    list_editable = ('is_top_pick',)

    def category_display(self, obj):
        return ", ".join([category.name for category in obj.category.all()])
    category_display.short_description = 'Categories'


class SoftwareInline(admin.TabularInline):
    model = Software.category.through
    extra = 1

class CategoryAdmin(admin.ModelAdmin):
    def software_count(self, obj):
        return Software.objects.filter(category=obj).count()

    list_display = ('name', 'description', 'software_count')
    search_fields = ('name', 'description')

    inlines = [SoftwareInline]


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'image')
    search_fields = ('title', 'content')
    list_filter = ('category',)
    list_editable = ('image',)


# Remove the CSVImportConf configuration as it's causing an error
# If CSV import functionality is needed, consider using a custom admin action
# or a management command instead


admin.site.register(Software, SoftwareAdmin)
admin.site.register(SoftwareCategory, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
