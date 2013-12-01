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
def add_tag(request):
        errors = []
        data={}
        if not 'tags' in request.POST or not request.POST['tags']:
                errors.append('please enter at least one tag')
        if not 'tack' in request.POST or not request.POST['tack']:
                errors.append('can not find tack')
        if not 'board' in request.POST or not request.POST['board']:
                errors.append('can not find board')
        this_board=TackdBoard.objects.get(pk=request.POST['board'])
        this_user=TwitterProfile.objects.get(user=request.user)
        if this_board.privacy is "private":
                if TackdBoard.objects.filter(pk=request.POST['board'], users=this_user)<1:
                        errors.append('You must be a member of this board to comment or post')
        if errors:
                data['errors']=errors
                return HttpResponse(json.dumps(data), content_type="application/json")
        tag_string=request.POST['tags']
        tags = tag_string.split(" ")
        this_tack=Tack.objects.get(pk=request.POST['tack'])
        for tag in tags:
            try:
                this_tack.tags.add(Tag.objects.get(pk=tag))
            except Tag.DoesNotExist:
                new_tag = Tag(value=tag)
                new_tag.save()
                this_tack.tags.add(new_tag)
        this_tack.save()
        all_tags = this_tack.tags.all()
        data['tags'] = []
        for atag in all_tags:
            data['tags'].append(atag.value)
        return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def search(request):
        context = {}
        errors=[]
        if not 'text' in request.POST or not request.POST['text']:
                errors.append('please enter a tag to search')
        if not 'board' in request.POST or not request.POST['board']:
                errors.append('can not locate board')
        this_user = TwitterProfile.objects.get(user=request.user)
        tag_term = request.POST['text']
        this_board = TackdBoard.objects.get(pk=request.POST['board'])
        if Tag.objects.filter(value=tag_term) < 1:
                errors.append('this tag does not exist')
        if errors:
                data={}
                data['errors']=errors
                return HttpResponse(json.dumps(data), content_type="application/json")
        tacks = Tack.objects.filter(board=this_board, tags=tag_term)
        context['tacks'] = tacks
        context['board'] = this_board
        return render(request, 'tackd/board.html', context)