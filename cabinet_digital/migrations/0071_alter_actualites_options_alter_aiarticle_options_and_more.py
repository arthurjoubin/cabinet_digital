# Generated by Django 5.1 on 2025-02-02 18:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet_digital', '0070_alter_aimodel_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='actualites',
            options={'verbose_name_plural': 'Logiciels - Actualités'},
        ),
        migrations.AlterModelOptions(
            name='aiarticle',
            options={'verbose_name': 'IA - Article', 'verbose_name_plural': 'IA - Articles'},
        ),
        migrations.AlterModelOptions(
            name='aitool',
            options={'verbose_name': 'IA - Outil', 'verbose_name_plural': 'IA - Outils'},
        ),
        migrations.AlterModelOptions(
            name='providerai',
            options={'verbose_name': 'IA - Editeurs', 'verbose_name_plural': 'IA - Editeurs'},
        ),
        migrations.DeleteModel(
            name='Article',
        ),
    ]
