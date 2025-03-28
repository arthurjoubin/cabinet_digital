# Generated by Django 5.1 on 2025-02-02 18:19

import django.db.models.deletion
import tinymce.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet_digital', '0061_aitoolcategory_aitool_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProviderAI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', tinymce.models.HTMLField(blank=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='providers/')),
                ('site', models.URLField(blank=True)),
                ('is_published', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Fournisseur IA',
                'verbose_name_plural': 'Fournisseurs IA',
            },
        ),
        migrations.AddField(
            model_name='aitool',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cabinet_digital.providerai'),
        ),
        migrations.AlterField(
            model_name='aimodel',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cabinet_digital.providerai'),
        ),
    ]
