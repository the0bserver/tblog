from django import forms
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from string import join
import os
from PIL import Image as PImage
from mysite.settings import MEDIA_ROOT, MEDIA_URL
from django.core.files import File
from os.path import join as pjoin
from tempfile import *

class Tag(models.Model):
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name

class Photo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    caption = models.CharField(max_length=100)
    tags = models.ManyToManyField(Tag, blank=True)
    user = models.ForeignKey(User)
    image = models.ImageField(upload_to='images/%Y/%m/%d')
    thumb = models.ImageField(upload_to='images/%Y/%m/%d', blank=True, null=True)
    # thumb2 = models.ImageField(upload_to="images/", blank=True, null=True)

    def save(self, *args, **kwargs):
        """Save image dimensions."""
        super(Photo, self).save(*args, **kwargs)
        im = PImage.open(pjoin(MEDIA_ROOT, self.image.name))
        # self.width, self.height = im.size

        # large thumbnail
        fn, ext = os.path.splitext(self.image.name)
        im.thumbnail((128,128), PImage.ANTIALIAS)
        thumb_fn = fn + "-thumb" + ext
        tf2 = NamedTemporaryFile()
        im.save(tf2.name, "JPEG")
        self.thumb.save(thumb_fn, File(open(tf2.name)), save=False)
        tf2.close()

        # small thumbnail
        # im.thumbnail((40,40), PImage.ANTIALIAS)
        # thumb_fn = fn + "-thumb" + ext
        # tf = NamedTemporaryFile()
        # im.save(tf.name, "JPEG")
        # self.thumbnail.save(thumb_fn, File(open(tf.name)), save=False)
        # tf.close()

        super(Photo, self).save(*args, **kwargs)

    def size(self):
        """Photo size."""
        return "%s x %s" % (self.image.width, self.image.height)

    def __unicode__(self):
        return self.image.name

    def tags_(self):
        lst = [x[1] for x in self.tags.values_list()]
        return str(join(lst, ', '))

    def thumbnail(self):
        return """<a href="%s/%s"><img border="0" alt="" src="%s/%s" height="40" /></a>""" % (
                                                                    (MEDIA_URL, self.image.name, MEDIA_URL, self.thumb.name))
    thumbnail.allow_tags = True

class Post(models.Model):
    title = models.CharField(max_length=60)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True)
    user = models.ForeignKey(User)
    photos = models.ManyToManyField(Photo, blank=True)
    def __unicode__(self):
        return self.title

    def preview(self):
        return unicode("%s..." % (self.body[:500]))
		
    def tags_(self):
        lst = [x[1] for x in self.tags.values_list()]
        return str(join(lst, ', '))

class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=60)
    body = models.TextField()
    post = models.ForeignKey(Post)
    def __unicode__(self):
        return unicode("%s" % (self.body[:60]))


### Admin classes

class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
	
class PhotoInline(admin.StackedInline):
    model = Photo
    extra = 5

class PostAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    display_fields = ["title"]
    list_display = ["title", "created", "user", "tags_"]
    list_filter = ["tags", "user"]
    exclude = ('user',)
    ordering = ('-created',)
    filter_horizontal = ('photos','tags',)
    
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
    list_display = ["post", "author", "created"]
    ordering = ('-created',)

class PhotoAdmin(admin.ModelAdmin):
    exclude = ('user','thumb',)
    # search_fields = ["title"]
    list_display = ["__unicode__", "user", "size", "tags_",
        "thumbnail", "created"]
    ordering = ('-created',)
    list_filter = ["tags", "user"]
    
    def save_model(self, request, obj, form, change): 
        obj.user = request.user
        obj.save()
		
admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Photo, PhotoAdmin)
