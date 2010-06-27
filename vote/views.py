from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from vote.models import Vote

VOTE = (('up', 1), ('down', -1), ('clear', 0))

@login_required
def vote_on_object(request, app, object_id, vote):
    """
    Generic object vote function
    """
    
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    
    try:
        app_label, model = app.split('.')
        ctype = ContentType.objects.get(app_label=app_label, model=model)
    except ContentType.DoesNotExist:
        return HttpResponseRedirect(next + '?error=app-not-exists')
        
    klass = ctype.model_class()
    
    try:
        Vote.objects.record_vote(klass.objects.get(pk=object_id), request.user, dict(VOTE)[vote])
    except klass.DoesNotExist:
        return HttpResponseRedirect(next + '?error=object-not-exists')
    except KeyError:
        return HttpResponseRedirect(next + '?error=vote-not-valid')
    except ValueError:
        return HttpResponseRedirect(next + '?error=vote-not-valid')
    
    return HttpResponseRedirect(next + '?success=vote-registered')
    