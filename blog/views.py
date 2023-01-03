from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from blog.models import Post, Comment
from django.core.paginator import Paginator
from blog.forms import EmailPostForm, CommentForm


def post_list(request):
    paginator = Paginator(Post.published.all(), 3)
    page_number = request.GET.get('page', 1)
    posts = paginator.page(page_number)
    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)  # Form for users to comment
    form = CommentForm()
    return render(request,
                  'blog/post/detail.html', {'post': post,
                                            'comments': comments, 'form': form})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{data['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {data['name']}\'s comments: {data['comments']}"
            send_mail(subject, message, 'your_account@gmail.com', [data['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, "blog/post/share.html", {"post": post, "form": form, "sent": sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    # A comment was posted
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database comment = form.save(commit=False)
        # Assign the post to the comment
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment})
