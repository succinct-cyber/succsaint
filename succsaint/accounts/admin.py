from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile
from django.utils.html import format_html

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'date_joined', 'last_login', 'is_admin')
    list_display_links = ('email', 'first_name', 'last_name')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border-radius: 50%;">'.format(object.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    list_display = ('user', 'city', 'state', 'country', 'thumbnail')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')                                                                                                                                                                                                                                                      

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
