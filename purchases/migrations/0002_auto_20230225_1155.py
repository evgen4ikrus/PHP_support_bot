# Generated by Django 3.2.7 on 2023-02-25 08:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='purchase',
            options={'get_latest_by': 'modified'},
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='price',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='product',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='status',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='user',
        ),
    ]