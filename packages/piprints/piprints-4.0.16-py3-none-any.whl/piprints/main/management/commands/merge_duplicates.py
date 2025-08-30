from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from piprints.main.models import *
from django.conf import settings

class Command(BaseCommand):
    args = ''
    help = 'merge duplicated person'

    def add_arguments(self, parser):
        parser.add_argument('--dry',
            action='store_true',
            dest='dry',
            default=False,
            help="don't touch the database")
        parser.add_argument('--confirm',
                    action='store_true',
                    dest='confirm',
                    default=False,
                    help="confirm you want to modify the database")

    def merge(self, clones):
        has_user = []
        for person in clones:
            counts = {}
            counts['TOTAL'] = 0
            for link, reverse in self.m2m_links:
                objects = getattr(person, link).all()
                counts[link] = objects.count()
                counts['TOTAL'] += counts[link]
            for link, reverse in self.o2m_links:
                objects = getattr(person, link).all()
                counts[link] = objects.count()
                counts['TOTAL'] += counts[link]
            if person.user:
                has_user.append(person)
            person.PREFERENCE = counts['TOTAL']
            print(("  person_id {} has {} related objects {}".format(person.id, counts['TOTAL'], 'and a user' if person.user else 'but no user')))
        if len(has_user) >1:
            print("person has multiple users: {}".format(' and '.join(["person id {} has user {}".format(person.id,person.user) for person in has_user])))
            print("arbitrarily using user {}".format(has_user[0].user))
        clones = sorted(clones, key=lambda person: -person.PREFERENCE)
        best_match = clones[0]
        for p in has_user:
            if p == best_match: continue
            user = has_user[0].user
            print(("   person_id", p.id, "remove user", user))
            print(("   person_id", best_match.id, "add user", user))
            if not self.dry:
                Person.objects.filter(id=p.id).update(**dict(user=None))
                Person.objects.filter(id=best_match.id).update(**dict(user=user))
        print(("  best match: {} user {}".format(best_match.id, best_match.user)))
        for person in clones:
            if person == best_match:
                continue
            print(("    merging person id {} related {}".format(person.id,person.PREFERENCE)))
            for link, reverse in self.m2m_links:
                # print "m2m", link
                objects = getattr(person, link).all()
                for object in objects:
                    print(("     ", link, object.id, "remove from", reverse, person.id, "add", best_match.id))
                    if not self.dry:
                        getattr(object, reverse).remove(person)
                        getattr(object, reverse).add(best_match)
            for link,reverse in self.o2m_links:
                # print "o2m", link
                objects = getattr(person, link).all()
                for object in objects:
                    print(("     ", object.id, link, getattr(object, 'person').id, "->", best_match.id))
                    if not self.dry:
                        type(object).objects.filter(id=object.id).update(**dict(person=best_match.id))
            if person.user:
                has_user.append(person)
            for field in ['email', 'affiliation', 'crm_id', 'arxiv_id', 'position', 'home_page', 'description']:
                value = getattr(person, field)
                if not getattr(best_match, field) and value:
                    print(("    update empty field {} of person_id {} with value {}".format(field, best_match.id, value).encode('utf8')))
                    if not self.dry:
                        setattr(best_match, field, value)
                        Person.objects.filter(id=best_match.id).update(**{field: value})
            print(("   delete person_id", person.id))
            if not self.dry:
                Person.objects.filter(id=person.id).delete()
                
        

    def handle(self, *args, **options):
        self.dry = options['dry']
        if not options['confirm'] and not self.dry:
            self.stdout.write("Please confirm using --confirm option or make a dry run with --dry")
            return
        self.m2m_links = []
        self.o2m_links = []
        self.m2o_links = []
        for field in Person._meta.get_fields():
            if field.many_to_many:
                if field.through._meta.auto_created:
                    self.m2m_links.append((field.get_accessor_name(), field.field.name))
                else:
                    pass # me lo ritrovo anche in one_to_many
            if field.one_to_many:
                self.o2m_links.append((field.get_accessor_name(), field.field.name))
            if field.many_to_one:
                self.m2o_links.append(field.name)
        
        # print self.m2m_links, self.o2m_links, self.m2o_links
                
        count = 0
        clones = []
        for person in Person.objects.all().order_by('lastname', 'firstname'):
            if clones and clones[0].lastname == person.lastname and clones[0].firstname == person.firstname:
                pass  # match!
            else:
                if clones:
                    if len(clones) > 1:
                        count += len(clones)
                        print(("merge {} {} clones ({})".format(clones[0].lastname, clones[1].firstname, len(clones)).encode('utf8')))
                        self.merge(clones)
                clones = []
            clones.append(person)
        if not count:
            print("no duplicates found")
