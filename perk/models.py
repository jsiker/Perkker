from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save
from django.template import Context, Template


class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    bio = models.TextField(null=True)

    def __unicode__(self):
        return "{}'s profile" .format(self.user.username)


def create_profile(sender, instance, created, **kwargs):
    """Callback to create user profile at time user is created,
    in case User doesn't create his/her own profile"""
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_profile, sender=User)


class VoteCountManager(models.Manager):
    def get_queryset(self):
        return super(VoteCountManager,
                     self).get_queryset().annotate(
                         votes=Count('vote')).order_by('-votes')


class Post(models.Model):
    title = models.CharField(max_length=100)
    submitter = models.ForeignKey(User)
    submitted_on = models.DateTimeField(auto_now_add=True)
    url = models.URLField("URL", max_length=200, blank=True)
    blurb = models.TextField(blank=True)
    with_votes = VoteCountManager()
    objects = models.Manager()   # default manager TK read docs

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': str(self.id)})


class Vote(models.Model):
    voter = models.ForeignKey(User)
    link = models.ForeignKey(Post)

    def __unicode__(self):
        return "{} upvoted {}" .format(self.voter.username, self.link.title)


_DiscussionTemplate = Template("""
<li>{{ discussion.message }}{% if replies %}
    <ul>
        {% for reply in replies %}
        {{ reply }}
        {% endfor %}
    </ul>
{% endif %}</li>
""".strip())


class Discussion(models.Model):
    message = models.TextField()
    reply_to = models.ForeignKey('self', related_name='replies',
        null=True, blank=True)

    @property
    def html(self):
        return _DiscussionTemplate.render(Context({
            'discussion': self,
            'replies': [reply.html() for reply in self.replies.all()]
        }))

