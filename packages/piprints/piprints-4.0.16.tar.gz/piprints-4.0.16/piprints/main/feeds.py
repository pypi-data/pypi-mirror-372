import datetime
import unicodedata

from django.contrib.syndication.views import Feed

from .models import Paper, Event, Seminar, News, Position
from piprints.settings import SITE_NAME

# From https://stackoverflow.com/a/19016117/807307
def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")

class MyFeed(Feed):
    def item_title(self, item):
        try:
            return remove_control_characters(item.feed_title())
        except AttributeError:
            return remove_control_characters(item.title)

    def item_description(self, item):
        try:
            return remove_control_characters(item.feed_description())
        except AttributeError:
            return remove_control_characters(item.description)
        

class LatestPapersFeed(MyFeed):
    title = "%s Papers" % SITE_NAME
    link = "/papers/"

    def items(self):
        #return Paper.objects.order_by('-creation_time')[1:2]
        return Paper.objects.order_by('-creation_time')[:20]


class ForthcomingEventsFeed(MyFeed):
    title = "%s Events" % SITE_NAME
    link = "/events/"

    def items(self):
        return Event.objects.order_by('date_from').filter(date_from__gte=datetime.date.today())


class ForthcomingSeminarsFeed(MyFeed):
    title = "%s Seminars" % SITE_NAME
    link = "/seminars/"

    def items(self):
        return Seminar.objects.order_by('date', 'time').filter(date__gte=datetime.date.today())


class LatestNewsFeed(MyFeed):
    title = "%s News" % SITE_NAME
    link = "/news/"

    def items(self):
        return News.objects.order_by('-creation_time').filter(creation_time__gt=datetime.datetime.now()-datetime.timedelta(30))[:10]


class OpenPositionsFeed(MyFeed):
    title = "%s Open Positions" % SITE_NAME
    link = "/positions/"

    def items(self):
        return Position.objects.order_by('deadline').filter(deadline__gte=datetime.date.today())

