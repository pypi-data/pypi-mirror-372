# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20160124_1803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='value',
            field=models.CharField(unique=True, max_length=16),
        ),
    ]
