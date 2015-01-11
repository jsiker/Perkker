from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from .models import Post, Vote, UserProfile
from forms import UserForm, UserProfileForm, PostForm

# Create your views here.


class PostListView(ListView):
    model = Post
    queryset = Post.with_votes.all()
    paginate_by = 10


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