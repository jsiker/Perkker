from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required as auth
from perk.views import PostListView, UserProfileDetailView, UserProfileEditView, PostCreateView, PostDetailView, \
    PostUpdateView, PostDeleteView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'perkville.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    ## registration ##
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),

    ##homepage##
    url(r'^$', PostListView.as_view(), name='home'),

    ##profile stuff##
    url(r'^users/(?P<slug>\w+)/$', UserProfileDetailView.as_view(), name='profile'),
    url(r'^edit_profile/$', auth(UserProfileEditView.as_view()), name="edit_profile"),

    ## post stuff##
    url(r'^post/create/$', auth(PostCreateView.as_view()), name='post_create'),
    url(r'^post/(?P<pk>\d+)/$', PostDetailView.as_view(), name='post_detail'),
    url(r'^post/update/(?P<pk>\d+)/$', auth(PostUpdateView.as_view()), name='post_update'),
    url(r'^post/delete/(?P<pk>\d+/$)', auth(PostDeleteView.as_view()), name='post_delete'),
    url(r'^comments/', include('django_comments.urls')),

)
