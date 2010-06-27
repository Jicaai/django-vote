from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.db import models

class VoteManager(models.Manager):
    def get_score(self, obj):
        """
        Get a dictionary containing the total score for ``obj`` and
        the number of votes it's received.
        """
        ctype = ContentType.objects.get_for_model(obj)
        result = self.filter(object_id=obj.pk,
                             content_type=ctype).aggregate(score=Sum('vote'), 
                                                           num_votes=Count('vote'))
        return result
    
    def record_vote(self, obj, user, vote):
        """
        Record a user's vote on a given object. Only allows a given user
        to vote once, though that vote may be changed.

        A zero vote indicates that any existing vote should be removed.
        """
        if vote not in (+1, 0, -1):
            raise ValueError('Invalid vote (must be +1/0/-1)')
        ctype = ContentType.objects.get_for_model(obj)
        try:
            v = self.get(user=user, content_type=ctype,
                         object_id=obj.pk)
            if vote == 0:
                v.delete()
            else:
                v.vote = vote
                v.save()
        except models.ObjectDoesNotExist:
            if vote != 0:
                self.create(user=user, content_type=ctype,
                            object_id=obj.pk, vote=vote)

    def get_top(self, Model, reverse=False):
        """
        Get the top scored objects for a given model.
        """
        ctype = ContentType.objects.get_for_model(Model)
        result = self.filter(content_type=ctype).values('object_id').annotate(score=Sum('vote')).order_by('%sscore' % ('' if reverse else '-'))
        return result
        
    def get_bottom(self, Model, reverse=True):
        return self.get_top(Model, reverse)

SCORES = (
    (u'+1', +1),
    (u'-1', -1),
)

class Vote(models.Model):
    user            = models.ForeignKey(User)
    content_type    = models.ForeignKey(ContentType)
    object_id       = models.PositiveIntegerField()
    content_object  = generic.GenericForeignKey('content_type', 'object_id')
    vote            = models.SmallIntegerField(choices=SCORES)

    objects = VoteManager()

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'),)
