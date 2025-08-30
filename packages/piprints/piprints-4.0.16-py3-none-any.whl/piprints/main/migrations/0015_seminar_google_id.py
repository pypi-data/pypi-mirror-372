# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20170428_2246'),
    ]

    operations = [
        migrations.AddField(
            model_name='seminar',
            name='google_id',
            field=models.CharField(default='', help_text='id of event in google calendar', max_length=30, blank=True),
        ),
    ]
