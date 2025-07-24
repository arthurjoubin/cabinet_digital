# Generated manually on 2025-07-06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet_digital', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactIntegrator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=200, verbose_name='Nom')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('entreprise', models.CharField(max_length=200, verbose_name="Nom de l'entreprise")),
                ('site_web', models.URLField(blank=True, verbose_name='Site web')),
                ('description', models.TextField(verbose_name='Description de votre activité')),
                ('logiciels_expertise', models.TextField(help_text='Quels logiciels maîtrisez-vous ?', verbose_name="Logiciels d'expertise")),
                ('zone_intervention', models.CharField(help_text='Région, département, national...', max_length=200, verbose_name="Zone d'intervention")),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('traite', models.BooleanField(default=False, verbose_name='Traité')),
            ],
            options={
                'verbose_name': 'Contact intégrateur entreprise',
                'verbose_name_plural': 'Contacts intégrateurs entreprises',
                'ordering': ['-date_creation'],
            },
        ),
    ]