import json
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, FormView
from .models import Post, Vote, UserProfile
from forms import UserProfileForm, PostForm, VoteForm

# Create your views here.


class PostListView(ListView):
    """Gets data from PostListView. If User is logged in, filters User's votes. Places those votes in a list called 'voted'
    to more easily manage who has voted for what."""
    model = Post
    queryset = Post.with_votes.all()
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            voted = Vote.objects.filter(voter=self.request.user)
            posts_in_page = [post.id for post in context["object_list"]]
            voted = voted.filter(link_id__in=posts_in_page)
            voted = voted.values_list('link_id', flat=True)
            context["voted"] = voted
        return context


class UserProfileDetailView(DetailView):
    """Gets user object from user model upon creation, creates profile and returns user"""
    model = get_user_model()
    slug_field = "username"
    template_name = "user_detail.html"

    def get_object(self, queryset=None):
        user = super(UserProfileDetailView, self).get_object(queryset)
        UserProfile.objects.get_or_create(user=user)
        return user


class UserProfileEditView(UpdateView):
    """Gets user object to ensure only logged in user can edit their own profile.
    Uses custom form to provide fields for profile update.
    Success URL returns to the same profile page upon edit."""
    model = UserProfile
    form_class = UserProfileForm
    template_name = "edit_profile.html"

    def get_object(self, queryset=None):
        return UserProfile.objects.get_or_create(user=self.request.user)[0]

    def get_success_url(self):
        return reverse("profile", kwargs={"slug": self.request.user})


class PostCreateView(CreateView):
    """Following Post classes use builtin Views for CRUD actions; sets score and submitter before saving into the
     database (commit=False)"""
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        f = form.save(commit=False)
        f.rank_score = 0.0
        f.submitter = self.request.user
        f.save()

        return super(CreateView, self).form_valid(form)


class PostDetailView(DetailView):
    model = Post


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm


class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy("home")


class JSONFormMixin(object):
    """Dict contains data we need, which is then turned into JSON object and then returned if valid"""
    def create_response(self, vdict=dict(), valid_form=True):
        response = HttpResponse(json.dumps(vdict), content_type='application/json')
        response.status = 200 if valid_form else 500
        return response


class VoteFormBaseView(FormView):
    form_class = VoteForm

    # overwrites above to return a http response (rather than a JSON object)
    def create_response(self, vdict=dict(), valid_form=True):
        response = HttpResponse(json.dumps(vdict))
        response.status = 200 if valid_form else 500
        return response

    # ties vote to post, vote to logged in user, filters on votes already cast
    def form_valid(self, form):
        post = get_object_or_404(Post, pk=form.data['link'])
        user = self.request.user
        prev_votes = Vote.objects.filter(voter=user, link=post)
        has_voted = (len(prev_votes) > 0)

        result = {"success": 1}
        if not has_voted:
            # add vote
            v = Vote.objects.create(voter=user, link=post)
            result["vote_obj"] = v.id
            print("Voted")
        else:
            # delete vote
            prev_votes[0].delete()
            result["unvoted"] = 1
            print("unvoted")
        return self.create_response(result, True)

    def form_invalid(self, form):
        print("invalid")
        result = {"success": 0, "form_errors": form.errors}
        return self.create_response(result, False)

"""combines the two (in theory to have both a JSON object and an HTTP return"""
class VoteFormView(JSONFormMixin, VoteFormBaseView):
    pass