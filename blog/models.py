from django import forms
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

class Tag(models.Model):
    tag = models.CharField(max_length=50)
    def __unicode__(self):
        return self.tag

class Photo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    caption = models.CharField(max_length=100)
    tags = models.ManyToManyField(Tag, blank=True)
    user = models.ForeignKey(User)
    posts = models.ManyToManyField(Post, blank=True)
    image = models.ImageField(upload_to='photo')
    def __unicode__(self):
        return unicode(self.pk)

class Post(models.Model):
    title = models.CharField(max_length=60)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    def __unicode__(self):
        return self.title

class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=60)
    body = models.TextField()
    post = models.ForeignKey(Post)
    def __unicode__(self):
        return unicode("%s" % (self.body[:60]))


### Admin classes

class TagAdmin(admin.ModelAdmin):
    list_display = ["tag"]

class PostAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    exclude = ('user',)
    def save_model(self, request, obj, form, change): 
        if self.model == Post:
            obj.user = request.user
        obj.save()
    def save_formset(self, request, form, formset, change): 
        if formset.model == Post:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.user = request.user
                instance.save()
        else:
            formset.save()


class CommentAdmin(admin.ModelAdmin):
    display_fields = ["post", "author", "created"]

class PhotoAdmin(admin.ModelAdmin):
    search_fields = ["caption", "tags"]
    exclude = ('user',)
    def save_model(self, request, obj, form, change): 
        if self.model == Photo:
            obj.user = request.user
        obj.save()

    def save_formset(self, request, form, formset, change): 
        if formset.model == Photo:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.user = request.user
                instance.save()
        else:
            formset.save()

admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Photo, PhotoAdmin)
