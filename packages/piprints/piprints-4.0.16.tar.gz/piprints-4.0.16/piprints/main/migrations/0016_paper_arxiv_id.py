# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_seminar_google_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='paper',
            name='arxiv_id',
            field=models.CharField(help_text=b'arxiv.org abstract identifier e.g. math/0611800', max_length=1024, blank=True),
        ),
    ]
