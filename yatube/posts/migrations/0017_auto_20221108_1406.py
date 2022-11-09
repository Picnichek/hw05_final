# Generated by Django 2.2.16 on 2022-11-08 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0016_auto_20221108_1405'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='couple_user_and_author_unique'),
        ),
    ]