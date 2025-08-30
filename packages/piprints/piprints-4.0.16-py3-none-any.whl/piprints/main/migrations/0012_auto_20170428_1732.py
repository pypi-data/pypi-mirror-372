# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_siteparameters_credits'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='google_id',
            field=models.CharField(default='', help_text='id of event in google calendar', max_length=30, blank=True),
        ),
        migrations.AddField(
            model_name='siteparameters',
            name='google_calendar_id',
            field=models.CharField(default='', help_text='set this if you have a google calendar associated with a service account', max_length=50, blank=True),
        ),
        migrations.AddField(
            model_name='siteparameters',
            name='google_service_account_credentials_json',
            field=models.TextField(default='', help_text='copy the json content of a google service account credentials', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(default='', help_text='if provided the event will be accessible with the URL http://email.com/<i>slug</i>', max_length=32, blank=True),
        ),
    ]
