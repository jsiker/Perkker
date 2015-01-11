from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Post, Vote, UserProfile
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    pass

admin.site.register(Post, PostAdmin)

class VoteAdmin(admin.ModelAdmin):
    pass

admin.site.register(Vote, VoteAdmin)

# creates stacked inline view for use in admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

#unites User with UserProfile, to just have one group in auth
class UserProfileAdmin(UserAdmin):
    inlines = (UserProfileInline,)

#unregister user model we're using (abstract or not)
admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserProfileAdmin)
