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

def add_notification(user, notification):
    twitter_user = TwitterProfile.objects.get(user=user)
    new_notification = Notification(user=twitter_user, text=notification, read=False)
    new_notification.save()

def notify_multiple_users(users, notification):
    for user in users:
        try:
            twitter_profile = TwitterProfile.objects.get(user=user)
            new_notification = Notification(user=twitter_profile, text=notification, read=False)
            new_notification.save()
        except TwitterProfile.DoesNotExist:
            continue

@login_required
def notifications(request):
    twitter_user = TwitterProfile.objects.get(user=request.user)
    notifications = Notification.objects.filter(user=twitter_user, read=False)
    notif_strings = []
    for notification in notifications:
        notif_data = {}
        notif_data['id'] = notification.id
        notif_data['text'] = notification.text
        notif_strings.append(notif_data)
    return HttpResponse(json.dumps(notif_strings), content_type="application/json")