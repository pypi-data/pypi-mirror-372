# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personrequest',
            name='ip',
            field=models.GenericIPAddressField(default=None, null=True, blank=True),
        ),
    ]
