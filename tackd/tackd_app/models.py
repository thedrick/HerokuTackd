from django.core.files import File
from django.db import models
from django.contrib.auth.models import User
from twython_django_oauth.models import *
import urllib
import os
import sys
    
class TackdBoard(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="board-photos")
    users = models.ManyToManyField(TwitterProfile, symmetrical=False, related_name="board_users")
    admin = models.ForeignKey(TwitterProfile, related_name="board_admin")
    privacy = models.CharField(max_length=20)

    def __unicode__(self):
        return self.title

class Comment(models.Model):
    text = models.TextField()
    user = models.ForeignKey(TwitterProfile)
    created = models.DateTimeField(auto_now_add=True)

class TackdProfile(models.Model):
    user = models.ForeignKey(TwitterProfile)
    image = models.ImageField(upload_to="profile-photos")


class Tag(models.Model):
    value = models.CharField(max_length=50, primary_key=True)

class Tack(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    author = models.ForeignKey(TwitterProfile, related_name="tackd_author")
    created = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=500)
    photo_url = models.CharField(max_length=1000)
    board = models.ForeignKey(TackdBoard)
    image = models.ImageField(upload_to="tack-photos")
    tags = models.ManyToManyField(Tag)
    comments = models.ManyToManyField(Comment)
    likes = models.ManyToManyField(TwitterProfile, symmetrical=False, related_name="tackd_lkes")
    def cache(self):
        """Store image locally if we have a URL"""
        if self.photo_url and self.photo_url['src'] != '' and not self.image:
            result = urllib.urlretrieve(self.photo_url['src'])
            self.image.save(
                    os.path.basename(self.photo_url['src']),
                    File(open(result[0]))
                    )
        self.save()

    def __unicode__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(TwitterProfile)
    text = models.CharField(max_length=500)
    action = models.CharField(max_length=200)
    read = models.BooleanField();

