# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_person_orcid_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteparameters',
            name='google_custom_search_id',
            field=models.CharField(default='', help_text='set this if you want a google custom search box', max_length=256, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='orcid_id',
            field=models.CharField(max_length=80, blank=True),
        ),
    ]
