# Generated by Django 5.1 on 2024-10-06 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet_digital', '0023_alter_article_category_alter_article_excerpt_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='is_published',
            field=models.BooleanField(default=True),
        ),
    ]
