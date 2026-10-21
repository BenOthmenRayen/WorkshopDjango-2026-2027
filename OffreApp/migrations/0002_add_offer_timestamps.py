import django.core.validators
import django.utils.timezone
from django.db import migrations, models


def populate_offer_timestamps(apps, schema_editor):
    Offre = apps.get_model('OffreApp', 'Offre')
    timestamp = django.utils.timezone.now()
    Offre.objects.filter(created_at__isnull=True).update(created_at=timestamp)
    Offre.objects.filter(updated_at__isnull=True).update(updated_at=timestamp)


class Migration(migrations.Migration):

    dependencies = [
        ('OffreApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='offre',
            name='created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='offre',
            name='updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(
            populate_offer_timestamps,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='offre',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='offre',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='offre',
            name='delai_jours',
            field=models.PositiveIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(
                        1,
                        message='Une valeur supérieure ou égale à 1 est requise',
                    )
                ],
            ),
        ),
    ]
