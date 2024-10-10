# Generated by Django 5.1.1 on 2024-09-29 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet_digital', '0020_viewer_software_viewers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='software',
            name='viewers',
        ),
        migrations.RenameField(
            model_name='software',
            old_name='unique_views',
            new_name='view_count',
        ),
        migrations.DeleteModel(
            name='Viewer',
        ),
    ]
