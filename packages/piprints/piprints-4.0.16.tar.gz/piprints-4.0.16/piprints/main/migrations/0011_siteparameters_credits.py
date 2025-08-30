# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_siteparameters_welcome_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteparameters',
            name='credits',
            field=models.TextField(blank=True),
        ),
    ]
