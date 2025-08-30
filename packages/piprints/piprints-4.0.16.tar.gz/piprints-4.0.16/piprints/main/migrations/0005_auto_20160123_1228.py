# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_researchproject_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(default='', help_text='if provided the event will be accessible with the URL http://cvgmt.sns.it/<i>slug</i>', max_length=32, blank=True),
        ),
    ]
