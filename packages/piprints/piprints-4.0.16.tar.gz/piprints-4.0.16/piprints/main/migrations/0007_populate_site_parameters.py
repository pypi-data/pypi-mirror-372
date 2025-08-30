# -*- coding: utf-8 -*-


from django.db import migrations, models
from django.contrib.sites.models import Site


def populate_site_parameters(apps, schema_editor):
    return
    # questa migrazione dà errore (2025-02-08)
    # serve veramente?

    Site = apps.get_model("sites", "Site")
    SiteParameters = apps.get_model("main", "SiteParameters")
    # the contrib.sites app creates the Site object
    # with a "postmigration" hook. So if this migration is executed 
    # in the first migration run, the Site tables will be empty...
    # So we need to create the Site object if it does not already exist
    Site.objects.update_or_create(
        pk=1,
        defaults={'domain': "example.com",
                  'name': "example.com"}
    )
    for site in Site.objects.filter(siteparameters=None):
        sp = SiteParameters.objects.create(domain=site.domain, name=site.name, site=site)

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20160124_1212'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_site_parameters, noop),
    ]
