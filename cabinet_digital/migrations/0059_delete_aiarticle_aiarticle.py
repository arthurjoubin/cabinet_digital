# Generated by Django 5.1 on 2025-01-26 20:40

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet_digital', '0058_aimodel_aitool_aiarticle_alter_software_description_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AIArticle',
        ),
        migrations.CreateModel(
            name='AIArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('excerpt', models.CharField(max_length=500)),
                ('content', models.TextField()),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('slug', models.SlugField(unique=True)),
                ('is_published', models.BooleanField(default=True)),
                ('banner', models.ImageField(blank=True, null=True, upload_to='articles/banners')),
                ('related_ai_models', models.ManyToManyField(blank=True, to='cabinet_digital.aimodel')),
                ('related_ai_tools', models.ManyToManyField(blank=True, to='cabinet_digital.aitool')),
            ],
            options={
                'verbose_name': 'Article IA',
                'verbose_name_plural': 'Articles IA',
            },
        ),
    ]
