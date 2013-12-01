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
def add_to_board(request):
        errors=[]
        if not 'username' in request.POST or not request.POST['username']:
                errors.append('please enter a tag to search')
        if not 'board' in request.POST or not request.POST['board']:
                errors.append('can not locate board')
        this_board =  TackdBoard.objects.get(pk=request.POST['board'])
        if TwitterProfile.objects.get(user=request.user) != this_board.admin:
                errors.append('must be board admin to add a member')
        if TwitterProfile.objects.filter(user__username=request.POST['username']) < 1:
                errors.append('this user does not exist')
        if errors:
                data={}
                data['errors']=errors
                return HttpResponse(json.dumps(data), content_type="application/json")
        new_member = TwitterProfile.objects.get(user__username=request.POST['username'])
        this_board.save()
        this_board.users.add(new_member)
        this_board.save()
        notification = "You have been added to board " + this_board.title + "."
        add_notification(new_member, notification)
        context = {}
        context['board'] = this_board
        board_tacks = Tack.objects.filter(board = this_board)
        context['tacks'] = board_tacks

        return render(request, 'tackd/board.html', context)
   
@login_required     
def all_users(request):
    twitters = TwitterProfile.objects.all()
    users = []
    for profile in twitters:
        datum = {}
        datum['value'] = profile.user.username
        datum['tokens'] = [profile.user.username]
        users.append(datum)
    return HttpResponse(json.dumps(users), content_type="application/json")