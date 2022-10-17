from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CommentForm, PostForm
from django.core.paginator import Paginator
from .models import Follow, Post, Group, User
from django.views.decorators.cache import cache_page


def page_not_found(request, exception):
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {
            "page": page,
            'paginator': paginator
         }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.order_by("-pub_date").filter(group=group)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {
            'group': group,
            "page": page,
            'paginator': paginator
        }
    )


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(data=request.POST, files=request.FILES or None)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    follows = author.following.all()
    print(request.user)
    for follow in follows:
        if request.user == follow.user:
            following = True
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'profile.html',
        {
            "page": page,
            "paginator": paginator,
            'author': author,
            "following": following
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    items = post.comments.all()
    form = CommentForm()
    return render(
        request,
        "post.html",
        {
            'post': post,
            'author': post.author,
            'items': items,
            'form': form
        }
    )


@login_required
def post_edit(request, username, post_id):
    edit_post = get_object_or_404(Post, pk=post_id)
    if edit_post.author == request.user:
        if request.method == "POST":
            form = PostForm(
                request.POST,
                files=request.FILES or None,
                instance=edit_post
            )
            if form.is_valid():
                form.save()
                return redirect("post", username, post_id)
        form = PostForm(instance=edit_post)
        return render(
            request,
            "new_post.html",
            {
                "form": form,
                "username": username,
                "post_id": post_id,
                "edit_post": edit_post
            }
        )
    return redirect("post", username, post_id)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = get_object_or_404(User, username=username)
    items = post.comments.all()
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            form = comment_form.save(commit=False)
            form.author = request.user
            form.post = post
            form.save()
            return redirect('post', username, post_id)
        return render(
            request,
            'post.html',
            {
                "post": post,
                'form': comment_form,
                "items": items
            }
        )
    form = CommentForm()
    return render(
        request,
        'post.html',
        {
            "author": author,
            "post": post,
            'form':form,
            "items": items
        }
    )


@login_required
def follow_index(request):
    user = get_object_or_404(User, username=request.user)
    subscriptions = user.follower.all()
    followings = []
    for subscription in subscriptions:
        followings.append(subscription.author)
    posts = Post.objects.filter(author__in=followings)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {
            'page': page,
            'paginator': paginator,
            'followings': followings
        }
    )


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=request.user)
    author = get_object_or_404(User, username=username)
    if user == author:
        return redirect('profile', username)
    for follow in author.following.all():
        if user == follow.user:
            return redirect('profile', username)
    Follow.objects.create(user=user, author=author)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=request.user)
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=user, author=author)
    follow.delete()
    return redirect('profile', username)
