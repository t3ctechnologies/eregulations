# Generated by Django 3.2.22 on 2023-10-06 15:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0032_auto_20230912_1345'),
        ('content_search', '0010_alter_contentindex_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentindex',
            name='fr_doc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='resources.federalregisterdocument'),
        ),
    ]