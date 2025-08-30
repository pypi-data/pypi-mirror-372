# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20170428_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteparameters',
            name='google_calendar_id',
            field=models.CharField(default='', help_text='set this if you have a google calendar associated with a service account', max_length=100, blank=True),
        ),
    ]
