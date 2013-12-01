from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'tackd_app.views.login',  name="twitter_login"),
  url(r'^home', 'tackd_app.views.home'),
  url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'tackd/login.html'}),
  url(r'^begin_auth', 'tackd_app.views.begin_auth'),
  url(r'^twitter_authenticate/?$', 'tackd_app.views.twitter_authenticate', name="twitter_callback"),
  url(r'^boards$', 'tackd_app.views.boards'),
  url(r'^new_board$', 'tackd_app.views.new_board'),
  url(r'^add_comment$', 'tackd_app.views.add_comment'),
  url(r'^add_tag$', 'tackd_app.views.add_tag'),
  url(r'^photo/(?P<id>\d+)$', 'tackd_app.views.board_photo', name='board_photo'),
  url(r'^board/(?P<id>\d+)$', 'tackd_app.views.board'),
  url(r'^search$', 'tackd_app.views.search'),
  url(r'^tack$', 'tackd_app.views.new_tack'),
  url(r'^tack_photo/(?P<id>\d+)$', 'tackd_app.views.tack_photo', name="tack_photo"),
  url(r'^add-to-board$', 'tackd_app.views.add_to_board'),
  url(r'^all_users$', 'tackd_app.views.all_users'),
  url(r'^notifications$', 'tackd_app.views.notifications'),
  url(r'^tweet$', 'tackd_app.views.tweet_tack'),
  url(r'^user-info/(?P<screen_name>\w+)', 'tackd_app.views.user_info'),
)
