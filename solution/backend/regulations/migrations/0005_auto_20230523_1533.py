# Generated by Django 3.2.18 on 2023-05-23 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regulations', '0004_statutelinkconverter'),
    ]

    operations = [
        migrations.AddField(
            model_name='statutelinkconverter',
            name='name',
            field=models.CharField(default='', max_length=512, verbose_name='Section Name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='statutelinkconverter',
            name='statute_title',
            field=models.CharField(default='', max_length=64, verbose_name='Statute Title'),
            preserve_default=False,
        ),
    ]