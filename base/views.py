from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.http import HttpResponse
from .models import Room, Topic, Message
from .forms import CreateRoomForm, CreateUserForm, EditProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# Create your views here.


def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    empty_activity = False
    empty_rooms = False

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )
    
    topics = Topic.objects.all()
    rooms_count = Room.objects.all().count()
    q_room_count = rooms.count()

    if q_room_count == 0:
        empty_rooms = True

    members_of_count = len(Room.objects.return_all_joned_rooms(request.user))
    remaining = rooms_count - members_of_count
    room_messages = Message.objects.filter(Q(room__name__icontains=q)).order_by("-created")[:20]

    if len(room_messages) == 0:
        empty_activity = True

    context = {
        "rooms": rooms,
        "topics": topics,
        "rooms_count": rooms_count,
        "room_messages": room_messages,
        'members_of_count':members_of_count,
        'remaining': remaining,
        'q_room_count':q_room_count,
        'empty_activity':empty_activity,
        'empty_rooms':empty_rooms,
    }
    return render(request, "base/home.html", context)


@login_required(login_url="login")
def rooms(request, pk):
    empty_activity = False
    room = Room.objects.get(id=pk)
    messages_ = room.message_set.all()
    members = room.members.all()
    topics = Topic.objects.all()
    room_messages = Message.objects.all().order_by("-created")[:20]
    if len(room_messages) == 0:
        empty_activity = True
    if request.method == "POST":
        message = request.POST.get("message")
        Message.objects.create(
            user=request.user,
            room=room,
            body=message,
        )
        if request.user not in room.members.all():
            room.members.add(request.user)

        return redirect("room", pk=room.id)
    context = {
        "room": room,
        "s_messages": messages_,
        "members": members,
        "room_messages": room_messages,
        'empty_activity': empty_activity,
        'topics':topics,
    }
    return render(request, "base/rooms.html", context)


@login_required(login_url="login")
def created_rooms(request):
    empty_activity = False

    room = Room.objects.return_all_created_rooms(request.user)
    topics = Topic.objects.all()
    room_messages = Message.objects.all().order_by("-created")[:20]
    if len(room_messages) == 0:
        empty_activity = True

    context = {
        "room_messages": room_messages,
        'empty_activity': empty_activity,
        'topics':topics,
        'rooms':room,
    }
    return render(request, 'base/created_rooms.html', context)


@login_required(login_url="login")
def update_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not authorized here")

    form = CreateRoomForm(request.POST or None, instance=room)
    if form.is_valid():
        form.save()
        return redirect("home")

    context = {
        "form": form,
    }
    return render(request, "base/create_room.html", context)


@login_required(login_url="login")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not authorized here")

    if request.method == "POST":
        room.delete()
        messages.success(request, 'Room deleted Successfully')
        return redirect("created-rooms")

    context = {
        "room": room,
    }
    return render(request, "base/delete_room.html", context)


def exit_room(request, pk):
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()

    if request.method == "POST":
        if request.user in room.members.all():
            room.members.remove(request.user)
            room.save()
            return redirect('room', pk=room.id)

    context = {
        'room':room,
        'topics':topics,
    }

    return render(request, 'base/exit_room.html', context)



@login_required(login_url="login")
def delete_message(request, pk):
    message = Message.objects.get(id=pk)
    topics = Topic.objects.all()

    if request.user != message.user:
        return HttpResponse("You are not authorized here")

    if request.method == "POST":
        message.delete()
        return redirect("room", pk=message.room.id)

    context = {
        "message": message,
        'topics':topics,
    }
    return render(request, "base/delete_room.html", context)


@login_required(login_url="login")
def create_room(request):
    empty_activity = False
    topics = Topic.objects.all()
    form = CreateRoomForm()
    room_messages = Message.objects.all().order_by("-created")[:20]
    if len(room_messages) == 0:
        empty_activity = True
    if request.method == "POST":
        form = CreateRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect("home")


    context = {
        "form": form,
        "topics": topics,
        "room_messages": room_messages,
        'empty_activity':empty_activity,
    }
    return render(request, "base/create_room.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.warning(request, "Username or Password does not exist")
        except:
            messages.warning(request, "User does not exist")

    return render(request, "base/login_page.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = CreateUserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data.get('username')
        user.save()
        messages.success(request, f"Account created for {username}")
        return redirect("login")

    context = {
        "form": form,
    }
    return render(request, "base/register.html", context)


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def profile_view(request, pk):
    topics = Topic.objects.all()
    user = User.objects.get(id=pk)
    form = EditProfileForm(request.POST or None, request.FILES or None, instance=user.profile)

    if form.is_valid():
        form.save()
        messages.success(request, "Profile has updated successfully")
        return redirect('profile', pk=user.id)
        

    context = {
        'topics':topics,
        "user":user,
        'form': form
    }
    return render(request, 'base/profile.html', context)