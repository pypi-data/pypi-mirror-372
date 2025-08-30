from django.core.management.base import BaseCommand

from piprints.main.models import Log, EmailMessage
from piprints.main.views import bulletin

class Command(BaseCommand):
    args = '<recipient>'
    help = 'Send weekly bulletin to the mailing list'

    def add_arguments(self, parser):
        parser.add_argument('to', type=str, nargs='+')
        parser.add_argument(
            '--dummy',
            action='store_true',
            dest='dummy',
            default=False,
            help="don't really send message", )

    def handle(self, *args, **options):
        dummy = options.get('dummy',False)
        c = bulletin()

        for to in options['to']:
            self.stdout.write('Sending email to %s\n' % to)
            message = EmailMessage(to=to)
            message.render_html('bulletin.html',c)
            message.render_template('mail/bulletin.mail',c)

            if not dummy:
                message.send()
            else:
                self.stdout.write('message not really sent (dummy option)')
                self.stdout.write(message.html_content)
                self.stdout.write(message.text_content)

            Log(action='send_bulletin',
                dump='Subject: %s, To: %s' % (message.subject,to)).save()
