# Generated by Django 3.1.6 on 2021-02-18 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hunt', '0004_auto_20210209_2241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='level',
            name='description',
            field=models.TextField(blank=True, default='', max_length=5000),
        ),
    ]