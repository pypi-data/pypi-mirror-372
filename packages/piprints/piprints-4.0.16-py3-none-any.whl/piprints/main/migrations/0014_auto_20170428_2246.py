# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20170428_2243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteparameters',
            name='google_calendar_id',
            field=models.CharField(default='', help_text='set this if you have a google calendar associated with a service account', max_length=1024, blank=True),
        ),
    ]
