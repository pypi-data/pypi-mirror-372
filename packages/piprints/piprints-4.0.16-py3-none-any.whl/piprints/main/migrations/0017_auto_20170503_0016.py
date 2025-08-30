# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_paper_arxiv_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='arxiv_id',
            field=models.CharField(max_length=250, blank=True),
        ),
        migrations.AlterField(
            model_name='paper',
            name='arxiv_id',
            field=models.CharField(max_length=1024, blank=True),
        ),
    ]
