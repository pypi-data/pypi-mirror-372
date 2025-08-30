# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20160124_2031'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteparameters',
            name='welcome_message',
            field=models.TextField(blank=True),
        ),
    ]
