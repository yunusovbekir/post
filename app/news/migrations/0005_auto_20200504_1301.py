# Generated by Django 3.0.4 on 2020-05-04 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_auto_20200430_1116'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-publish_date',), 'verbose_name': 'Post', 'verbose_name_plural': 'Posts'},
        ),
        migrations.AlterField(
            model_name='category',
            name='ordering',
            field=models.PositiveIntegerField(default=1, verbose_name='Ordering'),
        ),
        migrations.AlterField(
            model_name='content',
            name='content_type',
            field=models.CharField(choices=[('Main Text', 'Main Text'), ('Text', 'Text'), ('Accordion', 'Accordion'), ('Video', 'Video'), ('Gallery', 'Gallery'), ('Quote', 'Quote')], default='Main Text', max_length=255, verbose_name='Content type'),
        ),
        migrations.AlterField(
            model_name='content',
            name='ordering',
            field=models.PositiveIntegerField(default=1, verbose_name='Ordering'),
        ),
        migrations.AlterField(
            model_name='post',
            name='views',
            field=models.BigIntegerField(default=1, help_text='The number of views by visitors', verbose_name='Views'),
        ),
    ]
