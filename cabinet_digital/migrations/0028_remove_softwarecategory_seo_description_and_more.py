# Generated by Django 5.1 on 2024-10-07 18:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet_digital', '0027_tag_color_alter_tag_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='softwarecategory',
            name='seo_description',
        ),
        migrations.RemoveField(
            model_name='softwarecategory',
            name='seo_title',
        ),
    ]
