from typing import Any
from blog.models import Post, Comment
from blog.forms import CommentForm, PostForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from blog.decorators import create_update_delete_blogpost_permission_required
from i.decorators import user_comment_permission_required
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse


def PostListView(request):
    blog_posts = Post.objects.filter(status=1).order_by("-created_on")
    return render(request, "blog_home.html", {"blog_posts": blog_posts})


@login_required(login_url="Homepage:login")
@create_update_delete_blogpost_permission_required
def my_posts_list(request):
    logged_in_user = request.user
    if logged_in_user.user_type == "ADMINISTRATOR":
        posts = Post.objects.filter(status=1, post_admin=logged_in_user).order_by(
            "-created_on"
        )
    else:
        return render(
            request,
            "permission_denied.html",
            {"user_email": request.user.email},
        )
    return render(request, "myposts.html", {"posts": posts})


@login_required(login_url="Homepage:login")
@user_comment_permission_required
def live_post(request, slug):
    post = get_object_or_404(Post, slug=slug, status=1)
    comments = Comment.objects.filter(post=post, active=True)
    new_comment = None

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            new_comment.comments_user = (
                request.user
            )  # Assign the logged-in user to the comment
            new_comment.save()
            return redirect("blog:live_post", slug=post.slug)
        else:
            messages.error(
                request, "There was an error in your comment. Please try again."
            )
            return render(
                request,
                "live_post.html",
                {"blog_post": post, "comments": comments, "comment_form": comment_form},
            )
    else:
        comment_form = CommentForm()
    return render(
        request,
        "live_post.html",
        {"blog_post": post, "comments": comments, "comment_form": comment_form},
    )


class CreatePostView(LoginRequiredMixin, TemplateView):
    template_name = "blog_post.html"
    login_url = "Homepage:login"

    def get(self, request, *args, **kwargs):
        logged_in_user = self.request.user
        if logged_in_user.user_type == "ADMINISTRATOR":
            form = PostForm()
            return render(request, self.template_name, {"form": form})
        else:
            context = "create posts"
            return render(
                request,
                "permission_denied.html",
                {"user_email": request.user.email, "user_permission": context},
            )

    def post(self, request, *args, **kwargs):
        logged_in_user = self.request.user
        if logged_in_user.user_type == "ADMINISTRATOR":
            form = PostForm(request.POST)
            if form.is_valid():
                try:
                    post = form.save(commit=False)
                    post.author = request.user
                    post.post_admin = request.user

                    post.status = "1" if request.POST["status"] == "1" else "0"
                    post.save()

                    if post.status == "0":
                        messages.info(
                            request, "The post has been saved, but not active"
                        )
                        return redirect("blog:my_posts_list")
                    elif post.status == "1":
                        messages.info(request, "Successfully added a blog post")
                        return redirect("blog:live_post", slug=post.slug)
                except Exception as e:
                    return JsonResponse({"detail": str(e)})
            else:
                return render(request, self.template_name, {"form": form})
        else:
            context = "create posts"
            return render(
                request,
                "permission_denied.html",
                {"user_email": request.user.email, "user_permission": context},
            )
        return render(request, self.template_name, {"form": form})


@login_required(login_url="Homepage:login")
@create_update_delete_blogpost_permission_required
def update_post(request, slug):
    blog_post = get_object_or_404(Post, slug=slug, status=1)

    # if request.user == blog_post.post_admin:
    if request.method == "POST":
        form = PostForm(request.POST, instance=blog_post)
        if form.is_valid():
            form.save()
            return redirect("blog:live_post", slug=blog_post.slug)
        else:
            return render(
                request, "update_post.html", {"form": form, "blog_post": blog_post}
            )
    else:
        form = PostForm(instance=blog_post)
        return render(
            request, "update_post.html", {"form": form, "blog_post": blog_post}
        )


@login_required(login_url="Homepage:login")
@create_update_delete_blogpost_permission_required
def delete_post(request, slug):
    blog_post = get_object_or_404(Post, slug=slug, status=1)
    # if request.user.user_type == 'ADMINISTRATOR' and request.user == blog_post.post_admin:
    blog_post.delete()
    return redirect("blog:my_posts_list")


@login_required(login_url="Homepage:login")
@user_comment_permission_required
def update_comment(request, slug, comment_id):
    blog_post = get_object_or_404(Post, slug=slug, status=1)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.comments_user:
        messages.error(request, "You do not have permission to edit this comment.")
        return redirect("blog:blog_post")

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Your comment has been updated successfully.")
            return redirect("blog:live_post", slug=slug)
    else:
        form = CommentForm(instance=comment)
    return render(
        request,
        "update_comment.html",
        {"form": form, "comment": comment, "blog_post": blog_post},
    )


@login_required(login_url="Homepage:login")
@user_comment_permission_required
def delete_comment(request, slug, comment_id):
    # Get the comment to be deleted
    comment = get_object_or_404(Comment, pk=comment_id)

    # Check if the logged-in user is the author of the comment
    if comment.comments_user == request.user:
        # Delete the comment
        comment.delete()
        messages.success(request, "Your comment has been deleted.")
    else:
        # If the user is not the author, show an error message
        messages.error(request, "You do not have permission to delete this comment.")

    # Redirect back to the blog post or any other appropriate page
    return redirect("blog:live_post", slug=slug)


def search_view(request):
    all_post = Post.objects.all()
    context = {"count": all_post.count()}
    # return render(request, "base_post.html", context)
    return render(request, "blog_base.html", context)


def search_results_view(request):
    # query = request.GET.get("search", "")
    query = request.GET.get("search")
    print(f"{query = }")

    all_post = Post.objects.all()
    if query:
        post = all_post.filter(title__icontains=query, status=True)
    else:
        post = Post.objects.none()  # return empty queryset

    context = {"post": post, "count": post.count(), "query": query}
    return render(request, "search_results.html", context)


class Search_Results_For_Admin_My_Post(ListView):
    model = Post
    template_name = "admin_search_results_my_posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        queryset = super().get_queryset()

        filter_conditions = Q()

        search_requested = self.request.GET.get("search")
        if search_requested:
            filter_conditions = Q(title__icontains=search_requested)

        status_requested = self.request.GET.get("value")
        if status_requested:
            try:
                status_requested = int(status_requested)
                filter_conditions &= Q(status__exact=status_requested)
            except ValueError:
                filter_conditions &= Q(
                    status__exact=1
                )  # Or handle the error appropriately

        queryset = queryset.filter(filter_conditions)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_requested = self.request.GET.get("search")
        status_requested = self.request.GET.get("value")

        if status_requested is not None:
            status_requested = int(status_requested)
            context["status"] = "Publish" if status_requested == 1 else "Draft"
        else:
            context["status"] = "Nill"

        admin_post_detail = Post.admin_post_count(self, self.request.user)

        context["search"] = search_requested
        context["publish"] = admin_post_detail[0]
        context["draft"] = admin_post_detail[1]
        context["total"] = admin_post_detail[2]

        return context
