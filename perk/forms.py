from django import forms
from django.contrib.auth.models import User
from perk.models import UserProfile, Post, Vote


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio',)
        exclude = ('user',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ("submitter", "rank_score")


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote