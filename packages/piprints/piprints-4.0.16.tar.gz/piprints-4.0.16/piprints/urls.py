# -*- coding: utf8 -*-

import django
import django.views.static
from django.conf.urls import include
from django.urls import path
from django.conf.urls import handler404

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from rest_framework import routers
from .main import api_views

from .settings import MEDIA_ROOT

from .main import feeds, views

api_router = routers.DefaultRouter()
api_router.register(r'papers', api_views.PaperViewSet)

urlpatterns = []

if django.conf.settings.DEBUG:
    # only for development! Apache would serve these:
    urlpatterns += [
        path('media/<path>', django.views.static.serve,
         {'document_root': MEDIA_ROOT}),
#        path('static/(?P<path>.*)', django.views.static.serve,
#         {'document_root': STATIC_ROOT}),
        ]

urlpatterns += [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('robots.txt', views.robots_page),
    path('person/<int:id>/', views.person_page),
    path('person/<int:id>/arxiv', views.person_page),
    path('persons/', views.persons_page),
    path('papers/rss.xml', feeds.LatestPapersFeed()),
    path('papers/', views.papers_page),
    path('paper/<int:id>/', views.paper_page, name='paper'),
    path('newss/rss.xml', feeds.LatestNewsFeed()),
    path('newss/', views.newss_page),
    path('news/<int:id>/', views.news_page, name='news'),

    path('events/rss.xml', feeds.ForthcomingEventsFeed()),
    path('events/', views.events_page),
    path('event/<int:event_id>/registration', views.event_registration_page),
    path('event/<int:event_id>/participants', views.event_participants_page),
    path('event/<int:event_id>/timetable', views.event_timetable_page),
    path('event/<int:event_id>/speakers', views.event_speakers_page),
    path('event/<int:id>/', views.event_page, name='event'),
    path('seminars/rss.xml', feeds.ForthcomingSeminarsFeed()),
    path('seminars/', views.seminars_page),
    path('seminar/<int:id>/', views.seminar_page, name='seminar'),
    path('positions/rss.xml', feeds.OpenPositionsFeed()),
    path('positions/', views.positions_page),
    path('position/<int:id>/', views.position_page, name='position'),
    path('keyword/<int:id>/', views.keyword_page),
    path('users/', views.users_page),
    path('logs/', views.logs_page),
    path('login/', views.login_page),
    path('logout/', views.logout_page),
    path('edit/<str:model_name>/<int:id>/', views.edit_page),
    path('remove/<str:model_name>/<int:id>/', views.remove_page),
    path('add/<str:model_name>/', views.edit_page),
    path('upload/<str:model_name>/<int:id>/', views.upload_page),
    path('send/<str:model_name>/<int:id>/', views.send_page),
    path('passwd/<int:user_id>/', views.passwd_page),
    path('people/<str:path>', views.old_people_page),
    path('people/<str:path>/', views.old_people_page),
    path('request/', views.request_page),
    path('person_requests/', views.person_requests),
    path('person_request/<int:id>/', views.person_request),
    path('paper/list/', views.paper_list_page),
    path('bulletin/', views.bulletin_page),
    path('text_bulletin/', views.text_bulletin_page),
    path('credits/', views.default_page),
    path('mail/', views.default_page),
    path('cookies/', views.default_page),
    path('research/', views.default_page),
    path('version/', views.version_page),

    path('autocomplete/lastname/', views.autocomplete_lastname),  ## !!! hard-coded in static/js/edit_form.js
    path('autocomplete/firstname/', views.autocomplete_firstname),  ## !!! hard-coded in static/js/edit_form.js
    path('autocomplete/paper_type/', views.autocomplete_paper_type),
    path('autocomplete/position/', views.autocomplete_position),

    path('test_messages', views.test_messages_page),
    path('upload_curriculum', views.upload_curriculum_page),

    path('', views.main_page),

# interfaccia REST utilizzata ad esempio qui:
# https://aiquantum.uottawa.ca/papers.php

    path('api/', include(api_router.urls)),
    # path('api-auth/', include('rest_framework.urls'))
    path('research/', views.default_page),
    ]

# Wire up our API using automatic URL routing.
#urlpatterns += [
# Additionally, we include login URLs for the browsable API.
# url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
#]

# must be last!
urlpatterns += [
    path('<path:slug>', views.slug_page),
]

handler404 = views.page_not_found_view