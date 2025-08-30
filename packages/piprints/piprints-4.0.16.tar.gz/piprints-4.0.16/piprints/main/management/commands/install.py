import os, hashlib, subprocess, getpass
from optparse import make_option
from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string

from piprints import settings

def my_hash(s):
    for c in " \t\n":
        s=s.replace(c,'')
    return hashlib.md5(s).hexdigest()

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--install',
                    action='store_true',
                    dest='install',
                    default=False,
                    help='install file in /etc...'),
        make_option('--sudo',
                    action='store_true',
                    help='invoke sudo to create file if not existing'),
        )


    args = 'apache [--install]'
    help = 'create (and optionally install) apache configuration file. Uses checksum to not ruin modified files.'

    def handle(self, *args,**options):
        install = options['install']
        sudo = options['sudo']
        c = settings.__dict__
        for arg in args:
            if arg == 'apache':
                source = 'apache.conf'
                out = settings.APACHE_CONF
            else:
                print(('invalid command %s' % arg))
                
            s = render_to_string(source,c)
            old = s[:]
            hash = my_hash(s)
            s+='\n## This file automatically generated from %s. Checksum: ==%s==\n' % (
                source,hash)
            if install:
                if os.path.exists(out):
                ## check that it was not modified
                    content = file(out).readlines()
                    try:
                        hash = content[-1].split('==')[1]
                    except IndexError:
                        print(('File %s does not have an hash. Aborting...' % out))
                        return False
                    content = '\n'.join(content[:-1])
                    
                    if hash != my_hash(content):
                        print((len(content), len(old)))
                        print((content[:30],'...',content[-10:]))
                        print((old[:30],'...',old[-10:]))
                        print(('%s != %s' % (hash,my_hash(content))))
                        print(('File %s has been modified. Aborting...' % out))
                        return False
                else:
                    print(('File %s does not exist.' % out))
                    if sudo:
                        subprocess.check_call(['sudo','touch',out])
                        subprocess.check_call(['sudo','chown',getpass.getuser(),out]) 
                    else:
                        print('use --sudo option to invoke sudo for file creation')
                    
                file(out,'wb').write(s)
            else:
                print(s)
