# Generated by Django 5.1 on 2025-02-02 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet_digital', '0065_transition_provider_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='aimodel',
            name='provider_old',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
