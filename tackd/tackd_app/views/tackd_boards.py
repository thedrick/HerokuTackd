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
def new_board(request):
    errors = []
    if not 'title' in request.POST or not request.POST['title']:
        errors.append('Your board needs a title!')
    if not 'image' in request.FILES or not request.FILES['image']:
        errors.append('Your board needs a cover photo!')
    if not 'privacy' in request.POST or not request.POST['privacy']:
        errors.append('Your board needs a privacy setting!')
    if errors:
        data = {}
        data['errors'] = 'errors'
        return HttpResponse(json.dumps(data), content_type="application/json")
    context = {}
    user = TwitterProfile.objects.get(user=request.user)
    new_board = TackdBoard(title=request.POST['title'], image=request.FILES['image'], privacy=request.POST['privacy'], admin=user)
    new_board.save()
    new_board.users.add(user)
    new_board.save()
    context['board'] = new_board
    return render(request, 'tackd/board.html', context)

@login_required
def boards(request):
    context = {}
    curr_user = TwitterProfile.objects.get(user=request.user)
    boards = TackdBoard.objects.filter(users=curr_user)
    context['boards'] = boards
    return render(request, 'tackd/corkboard_template.html', context)

@login_required
def board(request, id):
    context = {}
    board = TackdBoard.objects.get(pk=id)
    tacks = Tack.objects.filter(board=board)
    if board.privacy is "secret":
            return render(request, 'tackd/corkboard_template.html', context)
    context['tacks'] = tacks
    context['board'] = board
    return render(request, 'tackd/board.html', context)

def board_photo(request, id):
    board = TackdBoard.objects.get(pk=id)
    if not board.image:
        raise Http404
    content_type = guess_type(board.image.name)
    return HttpResponse(board.image, mimetype=content_type)



