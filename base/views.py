from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Room, Topic, Message, User, Follow
from .forms import RoomForm, UserForm, MyUserCreationForm

from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from django.core.paginator import Paginator

def loginPage(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email = email, password = password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            
            # Set commit = False because we need to change the username to lower at the next lines
            user = form.save(commit=False)

            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An Error occurred during registration!')

    context = {'form': form}
    return render(request, 'base/login_register.html', context)

def home(request):
    if request.GET.get('q') != None:
        q= request.GET.get('q')
    else:
        q = ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) | 
        Q(name__icontains =q) |
        Q(description__icontains = q)
        )

    topics = Topic.objects.all()[0:5]

    room_count = rooms.count()
    room_messages = Message.objects.all().filter(Q(room__topic__name__icontains=q)).order_by('-created')[:9]

    # Paginator
    paginator = Paginator(rooms, 7)
    page_number = request.GET.get('page')
    rooms_of_the_page = paginator.get_page(page_number)

    context = {'rooms': rooms, 'topics': topics, 'room_count':room_count, 'room_messages': room_messages, 'rooms_of_the_page': rooms_of_the_page}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)

    # Take all the messages related to this room based on id
    room_messages = room.message_set.all()

    participants = room.participants.all()

    if request.method == 'POST':
        if request.POST.get('body', '').strip() == "":
            context = {'room': room, 'room_messages': room_messages, 'participants': participants}
            return render(request, 'base/room.html', context)

        message = Message.objects.create(
            user= request.user,
            room=room,
            body=request.POST.get('body')
        )

        room.participants.add(request.user)

        return redirect('room', pk=room.id)
    
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}

    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all().order_by('-created')[:5]
    topics = Topic.objects.all()
   

    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_follower=user)

    isFollowing = None
    if request.user.id != user.id:
        try:
            checkFollow = followers.filter(user=User.objects.get(pk=request.user.id))
            if len(checkFollow) != 0:
                isFollowing = True
            else:
                isFollowing = False
        except:
            isFollowing = False
    
    context = {
        'user': user,
        'rooms': rooms, 
        'room_messages': room_messages,
        'topics': topics,
        "following": following,
        "followers": followers,
        "isFollowing": isFollowing,
    }
    return render(request, 'base/profile.html', context)

def follow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    userfollowData = User.objects.get(username=userfollow)
    f = Follow(user=currentUser, user_follower=userfollowData)
    f.save()
    user_id = userfollowData.id
    return HttpResponseRedirect(reverse("user-profile", kwargs={'pk': user_id}))

def unfollow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    userfollowData = User.objects.get(username=userfollow)
    f = Follow.objects.get(user=currentUser, user_follower=userfollowData)
    f.delete()
    user_id = userfollowData.id
    return HttpResponseRedirect(reverse("user-profile", kwargs={'pk': user_id}))

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host = request.user,
            topic=topic,
            name=request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')


    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update_user.html', {
        'form': form
    })

def topicsPage(request):
    if request.GET.get('q') != None:
        q= request.GET.get('q')
    else:
        q = ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()[0:5]

    return render(request, 'base/activity.html', {'room_messages': room_messages})

@login_required
def videocall(request):
    return render(request, 'videocall.html', {'name': request.user.name})