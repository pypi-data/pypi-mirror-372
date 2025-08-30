# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20170520_1002'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='orcid_id',
            field=models.CharField(max_length=19, blank=True),
        ),
    ]
