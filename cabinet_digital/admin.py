from django.contrib import admin
from .models import (Software, SoftwareCategory, Actualites, Tag, Metier, AIModel, AIArticle, 
                     ProviderAI, Integrator, PlatformeDematerialisation, PDPSpecialtyTag, Company, Contact,
                     Integration, TypeIntegration, Module, ContactIntegrateur, ContactIntegrator)
from django.db import models
from django import forms
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages

# Imports Unfold
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget

# Configuration admin standard

# Configuration du site admin
admin.site.site_header = 'Cabinet Digital'
admin.site.site_title = 'Cabinet Digital Admin'
admin.site.index_title = 'Administration'

# User admin configuration removed since authentication is disabled

class ActualitesInline(admin.TabularInline):
    model = Actualites.tags.through
    extra = 1
    ordering = ('tag__name',)



class SoftwareInline(admin.TabularInline):
    model = Software.category.through
    extra = 1
    ordering = ('softwarecategory__name',)

class IntegratorInline(admin.TabularInline):
    model = Integrator.softwares.through
    extra = 0
    verbose_name = "Intégrateur"
    verbose_name_plural = "Intégrateurs"

@admin.register(Software)
class SoftwareAdmin(ModelAdmin):
    list_display = ['name', 'categories_list', 'integrators_count', 'description_truncated', 'is_top_pick', 'is_published', 'company']
    list_display_links = ['name']
    search_fields = ['name', 'description']
    list_filter = ['is_published', 'is_top_pick', 'category', 'company', 'integrators']
    list_editable = ['is_top_pick', 'company']
    filter_horizontal = ['category']
    inlines = [IntegratorInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Détails', {
            'fields': ('excerpt', 'category', 'logo', 'company'),
            'classes': ('collapse',)
        }),
        ('Publication', {
            'fields': ('is_published', 'is_top_pick'),
            'classes': ('collapse',)
        }),
        ('Liens', {
            'fields': ('site',),
            'classes': ('collapse',)
        }),
    )

    def categories_list(self, obj):
        return ", ".join([category.name for category in obj.category.all()])
    categories_list.short_description = 'Catégories'
    
    def integrators_count(self, obj):
        count = obj.integrators.count()
        if count > 0:
            return f"{count} intégrateur{'s' if count > 1 else ''}"
        return "Aucun"
    integrators_count.short_description = 'Intégrateurs'
    
    def description_truncated(self, obj):
        if obj.description:
            # Supprimer les balises HTML et tronquer à 100 caractères
            import re
            clean_text = re.sub('<.*?>', '', obj.description)
            if len(clean_text) > 100:
                return clean_text[:100] + "..."
            return clean_text
        return "Aucune description"
    description_truncated.short_description = 'Description'
    
    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }


    # Configuration standard Django admin

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

    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }

    compressed_fields = True
    warn_unsaved_form = True
    list_filter_sheet = True

@admin.register(Actualites)
class ActualitesAdmin(ModelAdmin):
    list_display = ['title', 'pub_date', 'is_published', 'company']
    list_filter = ['is_published', 'company']
    list_editable = ['is_published', 'company']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'content']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'excerpt')
        }),
        ('Publication', {
            'fields': ('is_published', 'pub_date', 'tags', 'company')
        }),
    )
    
    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }
    
    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }
    
    compressed_fields = True
    warn_unsaved_form = True

class TagAdminForm(forms.ModelForm):
    color = forms.CharField(widget=forms.TextInput(attrs={'type': 'color'}))

    class Meta:
        model = Tag
        fields = ['name', 'slug', 'color', 'seo_title', 'seo_description', 'seo_content', 'is_published']

@admin.register(Tag)
class TagAdmin(ModelAdmin):
    form = TagAdminForm
    list_display = ('name', 'slug', 'colored_tag', 'article_count', 'is_published')
    list_editable = ['slug', 'is_published']
    search_fields = ('name', 'seo_title')
    list_filter = ['is_published']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ActualitesInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'color', 'is_published')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description', 'seo_content'),
            'description': 'Optimisation pour les moteurs de recherche',
            'classes': ('collapse',)
        }),
    )

    def colored_tag(self, obj):
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 4px;">{}</span>',
            obj.color,
            '#000000' if obj.color == '#FFFFFF' else '#FFFFFF',
            obj.name
        )
    colored_tag.short_description = 'Tag'
    
    def article_count(self, obj):
        count = obj.actualites.filter(is_published=True).count()
        return f"{count} actualité{'s' if count > 1 else ''}"
    article_count.short_description = 'Actualités liées'
    
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
            'fields': ('is_published', 'is_top_pick'),
            'classes': ('collapse',)
        })
    )

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
            'fields': ('is_published', 'related_ai_models')
        }),
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

@admin.register(Integrator)
class IntegratorAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'count_softwares', 'softwares_list', 'tags', 'is_top_pick', 'is_published']
    list_display_links = ['name']
    search_fields = ['name', 'description', 'tags']
    list_filter = ['is_published', 'is_top_pick', 'softwares']
    list_editable = ['is_published', 'tags', 'is_top_pick']
    filter_horizontal = ['softwares']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Détails', {
            'fields': ('excerpt', 'tags', 'logo')
        }),
        ('Publication', {
            'fields': ('is_published', 'is_top_pick')
        }),
        ('Relations', {
            'fields': ('softwares', 'site'),
            'description': 'Logiciels que cet intégrateur peut implémenter'
        }),
    )
    
    def tags_display(self, obj):
        if obj.tags:
            tags = obj.get_tags_list()
            if len(tags) > 3:
                return f"{', '.join(tags[:3])}... (+{len(tags)-3})"
            return ', '.join(tags)
        return "Aucun tag"
    tags_display.short_description = 'Tags'
    
    def delete_model(self, request, obj):
        """Custom delete method to handle ManyToMany relationships properly"""
        from django.db import connection
        try:
            # Clear all ManyToMany relationships before deletion
            obj.softwares.clear()
            obj.pdp_platforms.clear()
            
            # Clean up orphaned relations in old tables
            with connection.cursor() as cursor:
                # Clean up old integrator_category relations if they exist
                try:
                    cursor.execute("DELETE FROM cabinet_digital_integrator_category WHERE integrator_id = ?", [obj.id])
                except Exception:
                    pass  # Table might not exist
                
                # Clean up any other orphaned relations
                try:
                    cursor.execute("DELETE FROM cabinet_digital_integratorcategory WHERE id IN (SELECT integratorcategory_id FROM cabinet_digital_integrator_category WHERE integrator_id = ?)", [obj.id])
                except Exception:
                    pass  # Table might not exist
            
            # Delete the object
            obj.delete()
            self.message_user(request, f"L'intégrateur '{obj.name}' a été supprimé avec succès.")
        except Exception as e:
            self.message_user(request, f"Erreur lors de la suppression: {str(e)}", level=messages.ERROR)
    
    def delete_queryset(self, request, queryset):
        """Custom bulk delete method"""
        from django.db import connection
        try:
            count = queryset.count()
            integrator_ids = list(queryset.values_list('id', flat=True))
            
            # Clean up orphaned relations in old tables for all integrators
            with connection.cursor() as cursor:
                # Clean up old integrator_category relations if they exist
                try:
                    placeholders = ','.join(['?' for _ in integrator_ids])
                    cursor.execute(f"DELETE FROM cabinet_digital_integrator_category WHERE integrator_id IN ({placeholders})", integrator_ids)
                except Exception:
                    pass  # Table might not exist
                
                # Clean up any other orphaned relations
                try:
                    cursor.execute(f"DELETE FROM cabinet_digital_integratorcategory WHERE id IN (SELECT integratorcategory_id FROM cabinet_digital_integrator_category WHERE integrator_id IN ({placeholders}))", integrator_ids)
                except Exception:
                    pass  # Table might not exist
            
            # Process each object individually to clear relationships
            for obj in queryset:
                # Clear all ManyToMany relationships before deletion
                obj.softwares.clear()
                obj.pdp_platforms.clear()
                # Delete the individual object
                obj.delete()
            self.message_user(request, f"{count} intégrateur(s) supprimé(s) avec succès.")
        except Exception as e:
            self.message_user(request, f"Erreur lors de la suppression en lot: {str(e)}", level=messages.ERROR)
    
    def count_softwares(self, obj):
        try:
            count = obj.softwares.count()
            # Debug: vérifier s'il y a des relations orphelines
            if count > 0:
                actual_softwares = obj.softwares.all()
                if not actual_softwares.exists():
                    return f"⚠️ {count} (relations orphelines)"
            return count
        except Exception as e:
            return f"Erreur: {str(e)}"
    count_softwares.short_description = 'Nombre de logiciels'
    
    def softwares_list(self, obj):
        try:
            # Debug: vérifier le nombre total
            total_count = obj.softwares.count()
            if total_count == 0:
                return "Aucun logiciel"
            
            # Récupérer les logiciels avec leurs noms
            softwares = obj.softwares.select_related().all()[:5]
            software_names = []
            
            for software in softwares:
                software_names.append(software.name)
            
            if software_names:
                result = ", ".join(software_names)
                if total_count > 5:
                    result += f" (+{total_count - 5} autres)"
                return result
            else:
                # Si on a un count mais pas de noms, il y a un problème de relation
                return f"⚠️ {total_count} logiciels (erreur d'affichage)"
                
        except Exception as e:
            return f"Erreur: {str(e)}"
    softwares_list.short_description = 'Logiciels liés'
    
    def get_deleted_objects(self, objs, request):
        """
        Personnalise l'affichage des objets qui seront supprimés
        pour montrer clairement les logiciels liés
        """
        deleted_objects, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)
        
        # Ajouter des informations détaillées sur les logiciels liés
        for obj in objs:
            if obj.softwares.exists():
                software_list = []
                for software in obj.softwares.all():
                    software_list.append(f"• {software.name}")
                
                if software_list:
                    deleted_objects.append(f"Logiciels liés à {obj.name}:")
                    deleted_objects.extend(software_list)
                    deleted_objects.append("⚠️ Ces relations seront supprimées mais les logiciels resteront intacts")
        
        return deleted_objects, model_count, perms_needed, protected
    
    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }
    
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_sheet = True

@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'website', 'is_published', 'updated_at']
    list_display_links = ['name']
    list_editable = ['slug', 'is_published']
    search_fields = ['name', 'description', 'excerpt']
    list_filter = ['is_published']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'logo', 'description', 'excerpt')
        }),
        ('Contact', {
            'fields': ('website',)
        }),
        ('Publication', {
            'fields': ('is_published',)
        }),
        ('Statistiques', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},
    }
    
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_sheet = True

@admin.register(PlatformeDematerialisation)
class PlatformeDematerialisationAdmin(ModelAdmin):
    list_display = ['name', 'company', 'excerpt', 'specialty_tags_display', 'slug']
    list_editable = ['excerpt', 'slug']
    list_filter = ['is_published', 'integrators', 'connected_softwares', 'company']
    search_fields = ['name', 'excerpt', 'specialty']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['integrators', 'connected_softwares']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'logo', 'excerpt', 'specialty', 'company', 'site')
        }),
        ('Relations', {
            'fields': ('integrators', 'connected_softwares')
        }),
        ('Publication', {
            'fields': ('is_published',)
        }),
        ('Statistiques', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def specialty_tags_display(self, obj):
        if obj.specialty:
            tags = obj.get_specialty_tags_list()
            if len(tags) > 3:
                return f"{', '.join(tags[:3])}... (+{len(tags)-3})"
            return ', '.join(tags)
        return "Aucune spécialité"
    specialty_tags_display.short_description = 'Spécialités'
    
    def integrators_list(self, obj):
        return ", ".join([integrator.name for integrator in obj.integrators.all()[:3]]) + ("..." if obj.integrators.count() > 3 else "")
    integrators_list.short_description = 'Intégrateurs'

@admin.register(PDPSpecialtyTag)
class PDPSpecialtyTagAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'pdp_count_display', 'is_published', 'updated_at']
    list_editable = ['is_published']
    search_fields = ['name']
    list_filter = ['is_published']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'is_published')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def pdp_count_display(self, obj):
        count = obj.get_pdp_count()
        return f"{count} PDP{'s' if count > 1 else ''}"
    pdp_count_display.short_description = 'Nombre de PDP'
    
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_sheet = True


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    list_display = ['nom', 'email', 'entreprise', 'message_preview', 'traite', 'date_creation']
    list_filter = ['traite', 'date_creation']
    search_fields = ['nom', 'email', 'message']
    readonly_fields = ['date_creation']
    list_editable = ['traite']
    
    fieldsets = (
        ('Message', {
            'fields': ('nom', 'email', 'entreprise', 'message')
        }),
        ('Gestion', {
            'fields': ('traite', 'date_creation')
        }),
    )
    
    def message_preview(self, obj):
        return obj.message[:100] + "..." if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Aperçu du message'
    
    compressed_fields = True
    warn_unsaved_form = True


@admin.register(ContactIntegrator)
class ContactIntegratorAdmin(ModelAdmin):
    list_display = ['nom', 'email', 'entreprise', 'zone_intervention', 'traite', 'date_creation']
    list_filter = ['traite', 'date_creation']
    search_fields = ['nom', 'email', 'entreprise', 'description']
    readonly_fields = ['date_creation']
    list_editable = ['traite']
    
    fieldsets = (
        ('Contact', {
            'fields': ('nom', 'email', 'entreprise')
        }),
        ('Entreprise', {
            'fields': ('zone_intervention', 'site_web')
        }),
        ('Expertise', {
            'fields': ('description', 'logiciels_expertise')
        }),
        ('Gestion', {
            'fields': ('traite', 'date_creation')
        }),
    )
    
    compressed_fields = True
    warn_unsaved_form = True
    list_filter_sheet = True


# Integration Admin Classes (merged from integrations app)

@admin.register(Module)
class ModuleAdmin(ModelAdmin):
    list_display = ['nom', 'slug', 'icone', 'ordre']
    list_editable = ['ordre']
    search_fields = ['nom', 'description']
    prepopulated_fields = {'slug': ('nom',)}
    ordering = ['ordre', 'nom']


@admin.register(TypeIntegration)
class TypeIntegrationAdmin(ModelAdmin):
    list_display = ['nom', 'slug']
    search_fields = ['nom']
    prepopulated_fields = {'slug': ('nom',)}





@admin.register(Integration)
class IntegrationAdmin(ModelAdmin):
    list_display = ['nom', 'logiciel_source', 'logiciel_destination', 'integrateur', 'actif', 'date_creation']
    list_filter = ['actif', 'type_integration', 'integrateur', 'modules', 'date_creation']
    search_fields = ['nom', 'description', 'logiciel_source__name', 'logiciel_destination__name', 'integrateur__name']
    prepopulated_fields = {'slug': ('nom',)}
    autocomplete_fields = ['logiciel_source', 'logiciel_destination', 'integrateur']
    filter_horizontal = ['modules']
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('nom', 'slug', 'logiciel_source', 'logiciel_destination', 'integrateur')
        }),
        ('Configuration', {
            'fields': ('type_integration', 'modules', 'actif')
        }),
        ('Contenu', {
            'fields': ('description', 'fonctionnalites')
        }),
        ('Informations complémentaires', {
            'fields': ('prix', 'url_documentation'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'logiciel_source', 'logiciel_destination', 'integrateur', 'type_integration'
        ).prefetch_related('modules')


@admin.register(ContactIntegrateur)
class ContactIntegrateurAdmin(ModelAdmin):
    list_display = ['nom', 'entreprise', 'type_contact', 'logiciel_source', 'logiciel_destination', 'traite', 'date_creation']
    list_filter = ['type_contact', 'traite', 'date_creation']
    search_fields = ['nom', 'entreprise', 'email', 'logiciel_source', 'logiciel_destination']
    readonly_fields = ['date_creation']
    list_editable = ['traite']
    
    fieldsets = (
        ('Contact', {
            'fields': ('nom', 'email', 'entreprise', 'type_contact', 'telephone')
        }),
        ('Intégration proposée', {
            'fields': ('logiciel_source', 'logiciel_destination', 'modules_concernes', 'description', 'url_documentation')
        }),
        ('Gestion', {
            'fields': ('traite', 'date_creation')
        }),
    )


