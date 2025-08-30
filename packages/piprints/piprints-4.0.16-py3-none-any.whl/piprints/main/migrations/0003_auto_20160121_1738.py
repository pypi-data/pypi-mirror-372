# -*- coding: utf-8 -*-


from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20160108_0818'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResearchProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('modification_time', models.DateTimeField(auto_now=True, null=True)),
                ('hidden', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=250)),
                ('principal_investigator', models.CharField(max_length=80, blank=True)),
                ('external_url', models.URLField(blank=True)),
                ('tag', models.CharField(max_length=80, blank=True)),
                ('hide', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(related_name='created_researchproject', default=None, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
                ('modified_by', models.ForeignKey(related_name='modified_researchproject', default=None, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.PROTECT)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='tag',
            name='value',
            field=models.CharField(unique=True, max_length=16, choices=[(b'tag1', b'tag1'), (b'tag2', b'tag2')]),
        ),
    ]
