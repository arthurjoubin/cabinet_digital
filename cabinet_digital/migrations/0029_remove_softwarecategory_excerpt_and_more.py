# Generated by Django 5.1 on 2024-10-07 18:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet_digital', '0028_remove_softwarecategory_seo_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='softwarecategory',
            name='excerpt',
        ),
        migrations.RemoveField(
            model_name='softwarecategory',
            name='last_modified',
        ),
    ]
