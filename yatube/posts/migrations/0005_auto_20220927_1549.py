# Generated by Django 2.2.9 on 2022-09-27 10:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20220927_1330'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={
                'ordering': ['-pub_date'],
                'verbose_name': 'Публикации',
                'verbose_name_plural': 'Публикации',
            },
        ),
    ]