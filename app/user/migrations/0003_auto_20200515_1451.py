# Generated by Django 3.0.4 on 2020-05-15 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20200515_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='user_type',
            field=models.IntegerField(choices=[(1, 'User'), (2, 'Reporter'), (3, 'Editor'), (4, 'Admin')], default=1, verbose_name='User type'),
        ),
    ]
