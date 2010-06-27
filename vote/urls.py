from django.conf.urls.defaults import *

urlpatterns = patterns('vote.views',
    url(r'^(?P<app>\w+)/(?P<object_id>\d+)/(?P<vote>(up|down|clear))/$', 'vote_on_object', name='vote-on-object'),
)