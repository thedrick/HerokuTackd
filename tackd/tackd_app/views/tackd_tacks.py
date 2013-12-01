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
def new_tack(request):
    errors = []
    if not 'url' in request.POST or not request.POST['url']:
        errors.append('please post a url')
    if not 'description' in request.POST or not request.POST['url']:
        errors.append('please add a description')
    if errors:
        data = {}
        data['errors'] = errors
        return HttpResponse(json.dumps(data), content_type="application/json")
    if not 'board' in request.POST or not request.POST['board']:
        print "BOARD NOT IN REQUEST"
        return render(request, 'tackd/board.html', {})
    curr_url = request.POST['url']
    curr_description = request.POST['description']
    metadata = parse_metadata(curr_url)
    curr_image = metadata['image']
    curr_title = metadata['title']
    board_id = request.POST['board']
    curr_board = TackdBoard.objects.get(pk=board_id)
    curr_author = TwitterProfile.objects.get(user=request.user)
    new_tack = Tack(url=curr_url, photo_url=metadata['photo'], description=curr_description, title=curr_title, board=curr_board, author=curr_author)
    new_tack.cache();
    # remove the image before sending data to the client
    metadata['image'] = None
    metadata['tackid'] = new_tack.id
    metadata['boardid'] = board_id
    #return render(request, json.dumps(metadata), content_type="application/json");
    return HttpResponse(json.dumps(metadata), content_type="application/json")

def tack_photo(request, id):
    tack = Tack.objects.get(pk=id)
    if not tack.image:
        raise Http404
    content_type = guess_type(tack.image.name)
    return HttpResponse(tack.image, mimetype=content_type)

@login_required
def edit_tack(request):
    errors = []
    data = {}
    data['errors'] = errors
    if not 'tack' in request.POST or not request.POST['tack']:
        errors.append("No tacks specified")
    if not 'description' in request.POST or not request.POST['description']:
        errors.append("You must provide a description (even if it's empty)")
    if not 'title' in request.POST or not request.POST['title']:
        errors.append("You most provide a title (even if it's empty)")
    if errors:
        return HttpResponse(json.dumps(data), content_type="application/json")
    title = request.POST['title']
    description = request.POST['description']
    tack = Tack.objects.get(pk=request.POST['tack'])
    if title.strip() != '':
        tack.title = title
    if description.strip() != '':
        tack.description = description
    tack.save()
    data['title'] = tack.title
    data['description'] = tack.description
    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def delete_tack(request):
    errors = []
    data = {}
    data['errors'] = errors
    if not 'tack' in request.POST or not request.POST['tack']:
        errors.append("You must specify which tack to delete.")
        data['success'] = False
        return HttpResponse(json.dumps(data), content_type="application/json")
    Tack.objects.get(pk=request.POST['tack']).delete()
    data['success'] = True
    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def add_comment(request):
    errors=[]
    if not 'text' in request.POST or not request.POST['text']:
            errors.append('please enter a comment')
    if not 'tack' in request.POST or not request.POST['tack']:
            errors.append('can not find tack')
    if not 'board' in request.POST or not request.POST['board']:
            errors.append('can not find board')
    this_board=TackdBoard.objects.get(pk=request.POST['board'])
    this_user=TwitterProfile.objects.get(user=request.user)
    if this_board.privacy is "private":
        if TackdBoard.objects.filter(pk=request.POST['board'], users=this_user) < 1:
            errors.append('You must be a member of this board to comment or post')
    if errors:
            data={}
            data['errors'] = errors
            return HttpResponse(json.dumps(data), content_type="application/json")
    this_text=request.POST['text']
    this_tack=Tack.objects.get(pk=request.POST['tack'])
    new_comment = Comment(text=this_text, user=this_user)
    new_comment.save()
    this_tack.save()
    this_tack.comments.add(new_comment)
    this_tack.save()
    comment_notif = this_user.user.username + " commented on tack " + this_tack.title + " in board " + this_board.title + "."
    notify_multiple_users(this_board.users.all().exclude(user=this_user), comment_notif)
    return HttpResponse(json.dumps({"username" : this_user.user.username}), content_type="application/json")