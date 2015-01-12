from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save


class UserProfile(models.Model):
    """Pulls from built-in User, adds a bio field"""
    user = models.OneToOneField(User, unique=True)
    bio = models.TextField(null=True)

    def __unicode__(self):
        return "{}'s profile" .format(self.user.username)


def create_profile(sender, instance, created, **kwargs):
    """Callback to create user profile at time user is created,
    in case User doesn't create his/her own profile; returns a tuple"""
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_profile, sender=User)


class VoteCountManager(models.Manager):
    """QuerySet to get all Votes and easily order by descending votes"""
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
    with_votes = VoteCountManager()   # Uses VoteCountManager to keep track of Vote objects on each Post
    objects = models.Manager()   # default manager to query Post.objects

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        """Used to generate URL @ post/post.id"""
        return reverse('post_detail', kwargs={'pk': str(self.id)})


class Vote(models.Model):
    voter = models.ForeignKey(User)
    link = models.ForeignKey(Post)

    def __unicode__(self):
        return "{} upvoted {}" .format(self.voter.username, self.link.title)




