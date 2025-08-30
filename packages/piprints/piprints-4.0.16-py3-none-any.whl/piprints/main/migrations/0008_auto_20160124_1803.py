# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_populate_site_parameters'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='siteparameters',
            options={'verbose_name_plural': 'site parameters'},
        ),
        migrations.AddField(
            model_name='siteparameters',
            name='title',
            field=models.CharField(max_length=250, blank=True),
        ),
    ]
