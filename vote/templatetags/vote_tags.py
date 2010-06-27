from django import template
from vote.models import Vote

register = template.Library()

class ScoreForObjectNode(template.Node):
    def __init__(self, obj, name):
        self.obj = template.Variable(obj)
        self.name = name

    def render(self, context):
        try:
            obj = self.obj.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        
        context[self.name] = Vote.objects.get_score(obj)
        return ''

@register.tag
def score_for_object(parser, token):
    """
    return the score for the object

    For example::

    {% score_for_object object as score %}
    {{ score.score }}
    {{ score.num_votes }}
    """
    
    bits = list(token.split_contents())
    if len(bits) != 4 or bits[2] != "as":
        raise template.TemplateSyntaxError("%r expected format is 'object as name'" % bits[0])
    obj     = bits[1]
    name    = bits[3]
    
    return ScoreForObjectNode(obj, name)

class VoteForUserNode(template.Node):
    def __init__(self, user, obj, name):
        self.user = template.Variable(user)
        self.obj = template.Variable(obj)
        self.name = name

    def render(self, context):
        try:
            user = self.user.resolve(context)
            obj = self.obj.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        context[self.name] = Vote.objects.get_for_user(user, obj)
        return ''

@register.tag
def vote_for_user(parser, token):
    """
    Retrieves the Vote by a user on a particular object

    For example::

    {% vote_by_user user on object as vote %}
    {{ vote }}
    
    """
    bits = list(token.split_contents())
    if len(bits) != 6 or bits[2] != "on" or bits[4] != "as":
        raise template.TemplateSyntaxError("%r expected format is 'user on object as name'" % bits[0])
    
    user    = bits[1]
    obj     = bits[3]
    name    = bits[5]
    
    return VoteForUserNode(user, obj, name)


