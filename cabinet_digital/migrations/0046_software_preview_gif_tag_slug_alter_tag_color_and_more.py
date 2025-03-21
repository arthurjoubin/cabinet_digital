# Generated by Django 5.1 on 2024-12-06 22:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet_digital', '0045_softwarecategory_excerpt'),
    ]

    operations = [
        migrations.AddField(
            model_name='software',
            name='preview_gif',
            field=models.ImageField(blank=True, null=True, upload_to='software_previews/'),
        ),
        migrations.AddField(
            model_name='tag',
            name='slug',
            field=models.SlugField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
