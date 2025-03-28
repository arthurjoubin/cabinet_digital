from django.contrib import admin
from .models import Software, SoftwareCategory, Actualites, Tag, Metier, AIModel, AITool, AIArticle, AIToolCategory, ProviderAI, UserProfile, Review, ReviewImage
from django.db import models
from django import forms
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.contrib import messages

from django.contrib.auth.models import User
from unfold.contrib.forms.widgets import WysiwygWidget

# Import admin.py first to test if it exists
import django.contrib.admin

# Mise à jour de l'admin utilisateur pour Unfold
class UnfoldUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


# Remplacer l'admin utilisateur par défaut
admin.site.unregister(User)
admin.site.register(User, UnfoldUserAdmin)

# Configuration du site admin
admin.site.site_header = 'Cabinet Digital'
admin.site.site_title = 'Cabinet Digital Admin'
admin.site.index_title = 'Administration'

class ActualitesInline(admin.TabularInline):
    model = Actualites.tags.through
    extra = 1
    ordering = ('tag__name',)



class SoftwareInline(admin.TabularInline):
    model = Software.category.through
    extra = 1
    ordering = ('softwarecategory__name',)

@admin.register(Software)
class SoftwareAdmin(ModelAdmin):
    list_display = ['name', 'categories_list', 'unique_views', 'metier', 'is_top_pick', 'is_published']
    list_display_links = ['name']
    search_fields = ['name', 'description']
    list_filter = ['is_published', 'is_top_pick', 'metier', 'category']
    list_editable = ['is_top_pick', 'metier', 'unique_views']
    readonly_fields = ['unique_views']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Détails', {
            'fields': ('excerpt', 'category', 'metier', 'logo', 'image_principale', 'preview_gif'),
            'classes': ('collapse',)
        }),
        ('Publication', {
            'fields': ('is_published', 'is_top_pick', 'unique_views'),
            'classes': ('collapse',)
        }),
        ('Liens', {
            'fields': ('site', 'video'),
            'classes': ('collapse',)
        }),
    )

    def categories_list(self, obj):
        return ", ".join([category.name for category in obj.category.all()])
    categories_list.short_description = 'Catégories'


    compressed_fields = True
    warn_unsaved_form = True
    list_filter_sheet = True
    list_horizontal_scrollbar_top = True


    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }

@admin.register(SoftwareCategory)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'software_count', 'excerpt', 'content_length', 'metier', 'is_published')
    list_editable = ['excerpt', 'metier', 'is_published']
    search_fields = ('name',)
    inlines = [SoftwareInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'excerpt', 'description', 'slug')
        }),
        ('Publication', {
            'fields': ('is_published', 'metier', 'icon'),
            'classes': ('collapse',)
        }),
    )

    def software_count(self, obj):
        return Software.objects.filter(category=obj).count()
    software_count.short_description = 'Nombre de logiciels'

    def content_length(self, obj):
        return f"{len(obj.description)} caractères"
    content_length.short_description = 'Longueur description'

    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }

    compressed_fields = True
    warn_unsaved_form = True
    list_filter_sheet = True

@admin.register(Actualites)
class ActualitesAdmin(ModelAdmin):
    list_display = ['title', 'pub_date', 'is_published']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'content']
    
    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }
    
    compressed_fields = True
    warn_unsaved_form = True

class TagAdminForm(forms.ModelForm):
    color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))

    class Meta:
        model = Tag
        fields = ['name', 'color']

@admin.register(Tag)
class TagAdmin(ModelAdmin):
    form = TagAdminForm
    list_display = ('name', 'slug', 'color', 'colored_tag')
    list_editable = ['slug']
    search_fields = ('name',)
    inlines = [ActualitesInline]


    def colored_tag(self, obj):
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 4px;">{}</span>',
            obj.color,
            '#000000' if obj.color == '#FFFFFF' else '#FFFFFF',
            obj.name
        )
    colored_tag.short_description = 'Tag'
    verbose_name = 'Logiciels - Tags'
    verbose_name_plural = 'Logiciels - Tags'


@admin.register(Metier)
class MetierAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'seo_title')
    list_filter = ['name']
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('name', 'slug')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description'),
            'description': 'Optimisation pour les moteurs de recherche',
            'classes': ('collapse',)
        }),
    )

    verbose_name = 'Logiciels - Métiers'
    verbose_name_plural = 'Logiciels - Métiers'

@admin.register(AIModel)
class AIModelAdmin(ModelAdmin):
    list_display = ['name', 'excerpt', 'tags', 'price', 'is_published']
    list_editable = ['excerpt', 'tags', 'price']
    search_fields = ['name', 'provider', 'description']
    list_filter = ['is_published', 'is_top_pick', 'provider']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'provider', 'description', 'excerpt', 'tags')
        }),
        ('Media', {
            'fields': ('logo', 'site'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_published', 'is_top_pick', 'unique_views'),
            'classes': ('collapse',)
        })
    )

    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }

    compressed_fields = True
    warn_unsaved_form = True
    list_filter_sheet = True

@admin.register(AIToolCategory)
class AIToolCategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'content_length']
    search_fields = ['name']
    
    def content_length(self, obj):
        return f"{len(obj.description)} caractères"
    content_length.short_description = 'Longueur description'
    
    def __str__(self):
        return self.name

@admin.register(AITool)
class AIToolAdmin(ModelAdmin):
    list_display = ['name', 'excerpt', 'categories_display', 'is_published']
    list_editable = ['excerpt']
    list_filter = ['name', 'category']
    search_fields = ['name', 'description']
    readonly_fields = ['unique_views']

    def categories_display(self, obj):
        return ", ".join([category.name for category in obj.category.all()])
    categories_display.short_description = 'Catégories'

    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }

    compressed_fields = True
    warn_unsaved_form = True
    list_filter_sheet = True

@admin.register(AIArticle)
class AIArticleAdmin(ModelAdmin):
    list_display = ['title', 'excerpt', 'tags', 'site', 'pub_date', 'is_published']
    list_editable = ['excerpt', 'tags', 'site']
    search_fields = ['title', 'content']
    list_filter = ['is_published', 'pub_date']
    date_hierarchy = 'pub_date'
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'banner')
        }),
        ('Publication', {
            'fields': ('is_published', 'related_ai_models', 'related_ai_tools')        }),
    )
    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }



@admin.register(ProviderAI)
class ProviderAIAdmin(ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    verbose_name = 'IA - Editeurs'
    verbose_name_plural = 'IA - Editeurs'

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0
    max_num = 5

@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ['title', 'software', 'user_display', 'rating', 'status', 'created_at']
    list_filter = ['status', 'rating', 'created_at', 'software']
    search_fields = ['title', 'content', 'user__userprofile__username', 'software__name']
    readonly_fields = ['created_at', 'updated_at', 'publish_date']
    list_editable = ['status', 'software', 'rating']
    actions = ['publish_reviews', 'reject_reviews', 'test_email_notification']
    inlines = [ReviewImageInline]
    
    fieldsets = (
        (None, {
            'fields': ('software', 'user', 'title', 'content', 'rating')
        }),
        ('Statut', {
            'fields': ('status', 'rejection_reason'),
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'publish_date'),
            'classes': ('collapse',),
        }),
    )
    
    def user_display(self, obj):
        return obj.user.userprofile.username
    user_display.short_description = 'Pseudo public'
    
    def publish_reviews(self, request, queryset):
        updated = queryset.update(status='published', publish_date=timezone.now())
        self.message_user(request, f"{updated} avis ont été publiés.")
    publish_reviews.short_description = "Publier les avis sélectionnés"
    
    def reject_reviews(self, request, queryset):
        # This needs custom logic with a reason, would be handled in a custom admin view
        pass
    reject_reviews.short_description = "Rejeter les avis sélectionnés"
    
    def test_email_notification(self, request, queryset):
        """Test sending an email notification for the selected review"""
        if queryset.count() != 1:
            self.message_user(request, "Veuillez sélectionner un seul avis pour tester l'envoi d'email.", messages.ERROR)
            return
            
        review = queryset.first()
        from cabinet_digital.utils import send_new_review_notification
        
        try:
            send_new_review_notification(review)
            self.message_user(request, f"Email de test envoyé avec succès pour l'avis '{review.title}'.", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Erreur lors de l'envoi de l'email: {str(e)}", messages.ERROR)
    
    test_email_notification.short_description = "Tester la notification email"


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ['username', 'user_email', 'created_at', 'last_active', 'review_count']
    search_fields = ['username', 'user__email']
    readonly_fields = ['created_at', 'last_active']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def review_count(self, obj):
        return obj.user.reviews.count()
    review_count.short_description = 'Nombre d\'avis'


