# Generated by Django 2.1.3 on 2019-02-27 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_auto_20190222_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, default=39.99, max_digits=20, null=True, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='product',
            name='upc',
            field=models.CharField(blank=True, max_length=12, null=True, verbose_name='barcode'),
        ),
    ]