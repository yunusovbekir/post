# Generated by Django 3.0.4 on 2020-05-18 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0010_post_top_news'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_multimedia',
            field=models.BooleanField(default=False, verbose_name='Multimedia Post'),
        ),
    ]
