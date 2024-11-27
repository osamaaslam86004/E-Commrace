from django.contrib import admin

from blog.forms import CommentFormAdmin
from blog.models import Comment, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "status", "created_on", "updated_on")
    list_filter = ("status",)
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ("title",)}

    # Organize fields into sections
    fieldsets = (
        ("Status", {"fields": ("status",)}),
        ("Basic Information", {"fields": ("title", "slug", "content")}),
    )


admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):

    form = CommentFormAdmin
    list_display = ("short_body", "post", "created_on", "active")
    list_filter = ("active", "created_on")
    search_fields = ("name", "email", "body")
    autocomplete_fields = ["post"]  # Enables search functionality for Post field
    actions = ["approve_comments"]

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "comments_user":
            kwargs["initial"] = request.user  # Set the current user as the default
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new comment
            obj.comments_user = request.user  # Automatically set the current user
        super().save_model(request, obj, form, change)

    # Method to show a truncated version of 'body'
    def short_body(self, obj):
        return obj.body[:50] + "..." if len(obj.body) > 50 else obj.body

    short_body.short_description = "Comment"


admin.site.register(Comment, CommentAdmin)
