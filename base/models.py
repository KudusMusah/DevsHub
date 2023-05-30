from django.db import models
from django.contrib.auth.models import User
import random

# Create your models here.
class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class RoomManager(models.Manager):
    def return_all_joned_rooms(self, user):
        rooms = []
        for room in Room.objects.all():
            if user in room.members.all() or room.host ==user:
                rooms.append(room)
        return rooms

    def return_all_created_rooms(self, user):
        rooms = []
        for room in Room.objects.all():
            if room.host == user:
                rooms.append(room)
        return rooms



class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    members = models.ManyToManyField(User, related_name="members", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = RoomManager()

    class Meta:
        ordering = ["-updated", "-created"]

    def __str__(self):
        return self.name

    def last_active(self):
        messages = self.message_set.all().order_by('-created')
        if messages:
            return messages[0].created
        else:
            return "No activity"

    def get_messages(self):
        return self.message_set.all()


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.body[:50]

    def get_random_color(self):
        colors = ["primary", "danger", "success", "dark", "info", "warning", "muted"]
        return random.choice(colors)

    class Meta:
        ordering = ["-created", '-updated']



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, blank=True)
    profile_pic = models.ImageField(default="avatar.png", upload_to='profiles/', blank=True)
    bio =  models.TextField(blank=True)
    job = models.CharField(max_length=150, blank=True)
    company = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

