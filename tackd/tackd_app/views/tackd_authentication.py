import json
from bs4 import BeautifulSoup
from tackd_app.getimages import *
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login as django_login
from django.contrib.auth import authenticate
from django.db import transaction
from django.http import HttpResponse, Http404
from mimetypes import guess_type
from django.core.urlresolvers import reverse
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.urlresolvers import reverse
from twython import Twython
from tackd_boards import *

from tackd_app.models import *

def home(request):
	return render(request, 'tackd/boards.html', {})

def login(request):
    if request.user and request.user.is_active:
        return boards(request)
    return render(request, 'tackd/login.html', {})

def begin_auth(request): 
    APP_KEY = "f0wDo5a57mSLYIuaIU4nZA"
    APP_SECRET = "XKgYeEng2G1qhVNhH3xae4r5LbDzcGD0QzRQp7nc"
    twitter = Twython(APP_KEY, APP_SECRET)
    callback_url = request.build_absolute_uri(reverse('tackd_app.views.twitter_authenticate'))
    auth = twitter.get_authentication_tokens(callback_url)
    request.session['request_token'] = auth
    auth_url = auth['auth_url']
    return HttpResponseRedirect(auth_url)

def twitter_authenticate(request):
    oauth_token = request.session['request_token']['oauth_token']
    oauth_token_secret = request.session['request_token']['oauth_token_secret']
    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET,
                      oauth_token, oauth_token_secret)

    authorized_tokens = twitter.get_authorized_tokens(request.GET['oauth_verifier'])

    # If they already exist log them in
    try:
        user = User.objects.get(username=authorized_tokens['screen_name'])
    except User.DoesNotExist:
        #if they don't, create a new django user. Placeholder for email, password is just the token
        user = User.objects.create_user(authorized_tokens['screen_name'], "placeholder@jfndjfn.com", authorized_tokens['oauth_token_secret'])
        profile = TwitterProfile()
        profile.user = user
        profile.oauth_token = authorized_tokens['oauth_token']
        profile.oauth_secret = authorized_tokens['oauth_token_secret']
        profile.save()

    user = authenticate(
        username=authorized_tokens['screen_name'],
        password=authorized_tokens['oauth_token_secret']
    )

    user.is_active = True

    #new: get the profile picture
    picture = twitter.show_user(screen_name=authorized_tokens['screen_name'])
    print("|            |           | " + str(picture))
    django_login(request, user)
    return HttpResponseRedirect('/tackd/home')
