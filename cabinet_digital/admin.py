from django.contrib import admin
from .models import Software, SoftwareCategory, Article

class SoftwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_display', 'editeur', 'description')
    list_filter = ('category', 'editeur')
    search_fields = ('name', 'description', 'editeur')

    def category_display(self, obj):
        return ", ".join([category.name for category in obj.category.all()])




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
    list_display = ('title', 'pub_date')
    search_fields = ('title', 'content')
    list_filter = ('category',)


admin.site.register(Software, SoftwareAdmin)
admin.site.register(SoftwareCategory, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)