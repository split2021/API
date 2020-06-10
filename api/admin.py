from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import path
from django import forms
import django.contrib.postgres.fields as postgres

from prettyjson import PrettyJSONWidget

from split.admin import split
from api.models import User, PaymentGroup, PaymentMethod, Log, PaymentGroupMembership, Friendship, Payment

# Register your models here.

class PaymentGroupMembershipInline(admin.TabularInline):
    """
    """

    model = PaymentGroupMembership
    extra = 1


class FriendshipInline(admin.TabularInline):
    """
    """

    model = Friendship
    extra = 1
    fk_name = "user1"

@admin.register(User, site=split)
class UserAdmin(DjangoUserAdmin):
    """
    Define admin model for custom User model with no email field.
    """

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'payment_methods', 'icon', 'image_tag')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'phone', 'username', 'first_name', 'last_name'),
        }),
    )
    filter_horizontal = ('friends', 'payment_methods', 'user_permissions', 'groups')
    readonly_fields = ('image_tag',)
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    inlines = (PaymentGroupMembershipInline, FriendshipInline)

    def image_tag(self, obj):
        return mark_safe(f'<img src="{obj.icon.url}" height="150", width="150"/>')
    image_tag.short_description = "User icon"


@admin.register(PaymentMethod, site=split)
class PaymentMethodAdmin(admin.ModelAdmin):
    """
    """
    list_display = ('name',)


class IsGroupEmptyListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('empty')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'isempty'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ("True", _("True")),
            ("False", _("False")),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == "True":
            return queryset.filter(users=None)
        elif self.value() == "False":
            return queryset.all().exclude(users=None)

@admin.register(PaymentGroup, site=split)
class PaymentGroupAdmin(admin.ModelAdmin):
    """
    """
    list_display = ('name', 'users_count')
    filter_horizontal = ('users',)
    list_filter = (IsGroupEmptyListFilter,)
    search_fields = ('name',)
    inlines = (PaymentGroupMembershipInline,)

    def users_count(self, instance):
        return instance.users.count()


@admin.register(Log, site=split)
class LogAdmin(admin.ModelAdmin):
    """
    """
    list_display = ('method', 'path', 'date')
    readonly_fields = ('path', 'method', 'body')
    formfield_overrides = {
        postgres.JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'}) }
    }


@admin.register(Payment, site=split)
class PaymentAdmin(admin.ModelAdmin):
    """
    """
    list_display = ('group', 'total', 'currency', 'target', 'is_complete', 'is_failed', 'is_refunded', 'calculate_payout_price')


@admin.register(Group, site=split)
class GroupAdmin(admin.ModelAdmin):
    """
    """
