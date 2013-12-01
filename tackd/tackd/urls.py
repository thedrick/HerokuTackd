from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', include('tackd_app.urls')),
    url(r'^tackd/', include('tackd_app.urls')),

)
