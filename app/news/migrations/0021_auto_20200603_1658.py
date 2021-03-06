# Generated by Django 3.0.4 on 2020-06-03 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0020_post_is_disliked_by_auth_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_disliked_by_auth_user',
            field=models.BooleanField(default=False, verbose_name='Disliked by Auth User'),
        ),
        migrations.AddField(
            model_name='comment',
            name='is_liked_by_auth_user',
            field=models.BooleanField(default=False, verbose_name='Liked by Auth User'),
        ),
    ]
