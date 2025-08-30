# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('main', '0005_auto_20160123_1228'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteParameters',
            fields=[
                ('site', models.OneToOneField(primary_key=True, serialize=False, to='sites.Site', on_delete=models.PROTECT)),
                ('title_banner', models.ImageField(upload_to='', blank=True)),
            ],
            bases=('sites.site',),
        ),
        migrations.AlterField(
            model_name='event',
            name='slug',
            field=models.SlugField(default='', help_text='if provided the event will be accessible with the URL http://localhost/<i>slug</i>', max_length=32, blank=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='value',
            field=models.CharField(unique=True, max_length=16, choices=[(b'tag1', b'tag1'), (b'tag2', b'tag2')]),
        ),
    ]
