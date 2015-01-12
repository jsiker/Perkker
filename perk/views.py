import json
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, FormView
from .models import Post, Vote, UserProfile
from forms import UserForm, UserProfileForm, PostForm, VoteForm
from registration.backends.simple.views import RegistrationView

# Create your views here.


# def users(request):
#     url = '/users/%s/' % request.user.username
#     return HttpResponseRedirect(url)


class PostListView(ListView):
    model = Post
    queryset = Post.with_votes.all()
    paginate_by = 10

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
    model = get_user_model()
    slug_field = "username"
    template_name = "user_detail.html"

    def get_object(self, queryset=None):
        user = super(UserProfileDetailView, self).get_object(queryset)
        UserProfile.objects.get_or_create(user=user)
        return user


class UserProfileEditView(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "edit_profile.html"

    def get_object(self, queryset=None):
        return UserProfile.objects.get_or_create(user=self.request.user)[0]

    def get_success_url(self):
        return reverse("profile", kwargs={"slug": self.request.user})


class PostCreateView(CreateView):
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
    def create_response(self, vdict=dict(), valid_form=True):
        response = HttpResponse(json.dumps(vdict), content_type='application/json')
        response.status = 200 if valid_form else 500
        return response


class VoteFormBaseView(FormView):
    form_class = VoteForm

    def create_response(self, vdict=dict(), valid_form=True):
        response = HttpResponse(json.dumps(vdict))
        response.status = 200 if valid_form else 500
        return response

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=form.data['link'])
        user = self.request.user
        prev_votes = Vote.objects.filter(voter=user, post=post)
        has_voted = (len(prev_votes) > 0)

        result = {"success": 1}
        if not has_voted:
            # add vote
            v = Vote.objects.create(voter=user, post=post)
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


class VoteFormView(JSONFormMixin, VoteFormBaseView):
    pass