from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('blog.views', 
    url(r'^admin/', include(admin.site.urls)),
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r"^(\d+)/$", "post"),
    (r"^month/(\d+)/(\d+)/$", "month"),
    (r"^add_comment/(\d+)/$", "add_comment"),
    (r"", "main"),
    (r"^delete_comment/(\d+)/$", "delete_comment"),
    ("^delete_comment/(\d+)/(\d+)/$", "delete_comment"),
)

# if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    # urlpatterns += patterns('',
    #    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
    #    'document_root': settings.STATIC_ROOT}))


urlpatterns += staticfiles_urlpatterns()
