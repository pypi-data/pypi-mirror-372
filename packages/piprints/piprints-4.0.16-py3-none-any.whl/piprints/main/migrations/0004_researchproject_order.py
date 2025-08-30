# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20160121_1738'),
    ]

    operations = [
        migrations.AddField(
            model_name='researchproject',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]
