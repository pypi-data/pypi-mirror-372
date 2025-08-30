# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20170503_0016'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteparameters',
            name='facebook_app_id',
            field=models.CharField(default='', help_text='set this if you have a facebook app id for the server', max_length=1024, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='user',
            field=models.OneToOneField(related_name='_person', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
