import time
from calendar import month_name
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from blog.models import *
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from mysite.settings import MEDIA_URL
from django.db.models import Count

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ["post"]

def main(request, f_tag=None, year=None, month=None):
    """Main listing."""
    if f_tag:
        posts = Post.objects.filter(tags__name=f_tag).order_by("-created")
    elif year:
        posts = Post.objects.filter(created__month=1, created__year=2013)
    else:
	    posts = Post.objects.all().order_by("-created")

    tags = Tag.objects.all().annotate(num_posts=Count('post')).order_by('-num_posts')
    paginator = Paginator(posts, 5)

    try: page = int(request.GET.get("page", '1'))
    except ValueError: page = 1
    
    try:
        posts = paginator.page(page)
    except (InvalidPage, EmptyPage):
        posts = paginator.page(paginator.num_pages)
    return render_to_response("blog/list.html", dict(posts=posts, user=request.user, is_auth=request.user.is_authenticated(),
    months=mkmonth_lst(), media_url=MEDIA_URL, f_tags=tags, f_tag=f_tag))

def add_comment(request, pk):
    """Add a new comment."""
    p = request.POST

    if p.has_key("body") and p["body"]:
        author = "Anonymous"
        if p["author"]: author = p["author"]

        comment = Comment(post=Post.objects.get(pk=pk))
        cf = CommentForm(p, instance=comment)
        cf.fields["author"].required = False

        comment = cf.save(commit=False)
        comment.author = author
        comment.save()
    return HttpResponseRedirect(reverse("blog.views.post", args=[pk]))

def post(request, pk):
    """Single post with comments and a comment form."""
    post = Post.objects.get(pk=int(pk))
    photos = post.photos.all()
    comments = Comment.objects.filter(post=post) 
    tags = Tag.objects.all().annotate(num_posts=Count('post')).order_by('-num_posts')
    d = dict(post=post, comments=comments, form=CommentForm(), photos=photos, f_tags=tags, media_url=MEDIA_URL, user=request.user)
    return render_to_response("blog/post/post.html", d, context_instance=RequestContext(request))

def mkmonth_lst():
    """Make a list of months to show archive links."""
    if not Post.objects.count(): return []

    # set up vars
    year, month = time.localtime()[:2]
    first = Post.objects.order_by("created")[0]
    fyear = first.created.year
    fmonth = first.created.month
    months = []

    # loop over years and months
    for y in range(year, fyear-1, -1):
        start, end = 12, 0
        if y == year: start = month
        if y == fyear: end = fmonth-1

        for m in range(start, end, -1):
            months.append((y, m, month_name[m]))
    return months

def month(request, year, month):
    """Monthly archive."""
    posts = Post.objects.filter(created__year=year, created__month=month)
    return render_to_response("blog/list.html", dict(posts=posts, user=request.user,
                                                months=mkmonth_lst(), archive=True))
												
def delete_comment(request, post_pk, pk=None):
    """Delete comment(s) with primary key `pk` or with pks in POST."""
    if request.user.is_staff:
        if not pk: pklst = request.POST.getlist("delete")
        else: pklst = [pk]

        for pk in pklst:
            Comment.objects.get(pk=pk).delete()
        return HttpResponseRedirect(reverse("blog.views.post", args=[post_pk]))
