import json
from bs4 import BeautifulSoup
from tackd_app.getimages import *
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse, Http404
from mimetypes import guess_type
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.urlresolvers import reverse
from twython import Twython

from tackd_app.models import *

@login_required
def tweet_tack(request):
        if not 'tack' in request.POST or not request.POST['tack']:
                errors.append('could not locate tack')
        this_tack=Tack.objects.get(pk=request.POST['tack'])
        this_user = this_tack.author
        APP_KEY = "f0wDo5a57mSLYIuaIU4nZA"
        APP_SECRET = "XKgYeEng2G1qhVNhH3xae4r5LbDzcGD0QzRQp7nc"
        twitter = Twython(APP_KEY, APP_SECRET ,this_user.oauth_token, this_user.oauth_secret)
        twitter.verify_credentials()
        twitter.get_home_timeline()
        if not this_tack.image:
                twitter.update_status(status=this_tack.description)
        else:
                photo = this_tack.image.file
                twitter.update_status_with_media(status=this_tack.description, media=photo)
        return render(request, 'tackd/corkboard_template.html', {})

@login_required
def user_info(request, screen_name):
        try:
                django_user = User.objects.get(username=screen_name)
                current_user = TwitterProfile(user=django_user)
                APP_KEY = "f0wDo5a57mSLYIuaIU4nZA"
                APP_SECRET = "XKgYeEng2G1qhVNhH3xae4r5LbDzcGD0QzRQp7nc"
                twitter = Twython(APP_KEY, APP_SECRET, current_user.oauth_token, current_user.oauth_secret)
                return HttpResponse(json.dumps(twitter.show_user(screen_name=screen_name)), content_type="application/json")
        except:
                return HttpResponse(json.dumps({"errors" : "Count not find user " + screen_name}), content_type="application/json")