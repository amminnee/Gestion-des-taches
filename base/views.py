from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import User, Project, Profile, Task, Message, Invit, Notification
from .forms import LoginForm, RegisterForm, ProjectForm, TaskForm, ProfileForm, UserForm


def unread(request):
    unread = Notification.objects.filter(receivers=request.user).count() - Notification.objects.filter(readers=request.user).count()
    return unread

@login_required(login_url='login')
def projects(request):
    user = request.user
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    projects = Project.objects.filter((Q(host=user) | Q(participants = user)) & Q(title__icontains=q)).distinct()

    context = {'unread': unread(request), 
               'activity_msgs': Message.objects.all().order_by('-created')[0:10], 
               'projects': projects, 
               'user': user,
               'selected': 'P',
               }
    return render(request, 'base/projects.html', context)


def login_user(request):
    if request.user.is_authenticated:   
        return redirect("projects")

    if request.method == 'POST':
        user = None
        email = request.POST['email'].lower()
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('projects')
            else:
                messages.error(request, "Mot de passe incorrecte")
        except:
            messages.error(request, 'Adresse email invalide')
            
    form = LoginForm()
    context = {'activity_msgs': Message.objects.all().order_by('-created')[0:10], 'form': form}
    return render(request, 'base/login.html', context)


def register_user(request):
    form = RegisterForm()
    invalide_fields = None

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('projects')
        else:
            invalide_fields = form.errors.keys()
            messages.error(request, "Veuillez ressayer")

    context = {'activity_msgs': Message.objects.all().order_by('-created')[0:10], 'form': form, 'errors': invalide_fields}
    return render(request, 'base/register.html', context)


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('login')



@login_required(login_url='login')
def create_project(request):
    form = ProjectForm()
    btn = 'Créer'
    if request.method== 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.host = request.user
            project.save()
            project.participants.add(request.user)
            return redirect('projects')
        else:
            messages.error(request,"an error has occured")
    context = {'unread': unread(request), 'activity_msgs': Message.objects.all().order_by('-created')[0:10], 'form': form, 'btn': btn, 'project': 'Nouveau projet'}
    return render(request, 'base/project_form.html', context)


@login_required(login_url='login')
def update_project(request, pk):
    project = Project.objects.get(id=pk)
    form = ProjectForm(instance=project)
    btn = 'Sauvegarder'
    users = 'Participants'

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            return redirect('projects')

    context = {'unread': unread(request), 'activity_msgs': Message.objects.all().order_by('-created')[0:10], 'form': form, 'btn': btn, 'project': project, 'object': project, 'users': users}
    if request.user == project.host:
        return render(request, 'base/project_form.html', context)
    else:
        return redirect('projects')
    

@login_required(login_url='login')
def delete_project(request, pk):
    object_name = 'le projet'
    project = Project.objects.get(id=pk)
    object = project
    users = 'Participants'
    name = project.title

    if request.method == 'POST':
        project.delete()
        return redirect('projects')

    context = {'unread': unread(request), 'activity_msgs': Message.objects.all().order_by('-created')[0:10], 'object_name': object_name, 'name': name, 'object': object, 'users': users}
    if request.user == project.host:
        return render(request, 'base/delete.html', context)
    else:
        return redirect('projects')
    

@login_required(login_url='login')
def project_tasks(request, pk):
    project = Project.objects.get(id=pk)
    users = 'Participants'
    q = request.GET.get('q')
    if q:
        tasks = project.task_set.all().filter(status=q)
    else:
        tasks = project.task_set.all()

    context = {'unread': unread(request), 
               'activity_msgs': Message.objects.all().order_by('-created')[0:10], 
               'project': project, 
               'object': project, 
               'users': users, 
               'tasks': tasks, 
               'task': 'project_tasks',
               'selected': 'T',
               'filter': q,
               }
    if request.user in project.participants.all():
        return render(request, 'base/tasks.html', context)
    else:
        return redirect('projects')
    

@login_required(login_url='login')
def project_description(request, pk):
    project = Project.objects.get(id=pk)
    users = 'Participants'

    context = {'unread': unread(request), 
               'activity_msgs': Message.objects.all().order_by('-created')[0:10], 
               'project': project, 
               'object': project, 
               'users': users,
               'selected': 'D',
               }
    if request.user in project.participants.all():
        return render(request, 'base/project_description.html', context)
    else:
        return redirect('projects')    
    


@login_required(login_url='login')
def tasks(request):
    q = request.GET.get('q')
    if q:
        tasks = Task.objects.all().filter(participants=request.user, status=q)
    else:
        tasks = Task.objects.all().filter(participants=request.user)

    context = {'unread': unread(request), 
               'activity_msgs': Message.objects.all().order_by('-created')[0:10], 
               'tasks': tasks, 
               'my_tasks': True, 
               'task': 'tasks',
               'selected': 'T',
               'filter': q,
               }
    return render(request, 'base/tasks.html', context)  


@login_required(login_url='login')
def create_task(request, pk):
    form = TaskForm()
    project = Project.objects.get(id=pk)
    btn = 'Créer'
    users = 'Participants'

    if request.method== 'POST':
        task = Task.objects.create(title='temp', project=project)
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            return redirect('project_tasks', pk=pk)
        else:
            task.delete()
            messages.error(request,"Erreur, veuillez ressayer")

    context = {'unread': unread(request), 'activity_msgs': Message.objects.all().order_by('-created')[0:10], 'form': form, 'btn': btn, 'project': project, 'object': project, 'users': users}
    if request.user == project.host:
        return render(request, 'base/task_form.html', context)
    else:
        return redirect('projects')


@login_required(login_url='login')
def update_task(request, pk1, pk2):
    project = Project.objects.get(id=pk1)
    task = Task.objects.get(id=pk2)
    form = TaskForm(instance=task)
    btn = 'Sauvegarder'
    users = 'Collaborateurs'

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            return redirect('project_tasks', pk=pk1)

    context = {'unread': unread(request), 'activity_msgs': Message.objects.all().order_by('-created')[0:10], 'form': form, 'btn': btn, 'project': project, 'object': task, 'users': users, 'task': task}
    if request.user == project.host:
        return render(request, 'base/task_form.html', context)
    else:
        return redirect('projects')
    

@login_required(login_url='login')
def task_description(request, pk1, pk2):
    project = Project.objects.get(id=pk1)
    task = Task.objects.get(id=pk2)
    users = 'Collaborateurs'

    if task.status == 'C':
        value = 'Terminer'
    else:
        value = 'Commencer'

    status = {'Commencer': 'C', 'Terminer': 'T'}

    if request.method == 'POST':
        task.status = status[value]
        task.save()
        if task.status == 'T':
            notification = Notification.objects.create(
                title='T',
                task=task,
            )
            notification.receivers.set(task.project.participants.all())

        return redirect('task_description', pk1=pk1, pk2=pk2)

    context = {'unread': unread(request), 'activity_msgs': Message.objects.all().order_by('-created')[0:10], 'project': project, 'object': task, 'users': users, 'task': task, 'value': value}
    if request.user in task.participants.all() or request.user == project.host:
        return render(request, 'base/task_description.html', context)
    else:
        return redirect('projects') 
    

@login_required(login_url='login')
def delete_task(request, pk1, pk2):
    object_name = 'la tache'
    task = Task.objects.get(id=pk2)
    project = Project.objects.get(id=pk1)
    name = task.title
    object = task
    users = 'Collaborateurs'

    if request.method == 'POST':
        task.delete()
        return redirect('project_tasks', pk=pk1)

    context = {'unread': unread(request), 'activity_msgs': Message.objects.all().order_by('-created')[0:10], 'object_name': object_name, 'name': name, 'object': object, 'users': users, 'task': task}
    if request.user == project.host:
        return render(request, 'base/delete.html', context)
    else:
        return redirect('projects')
    

@login_required(login_url='login')
def add_user(request, pk1, pk2):
    task = Task.objects.get(id=pk2)
    project = Project.objects.get(id=pk1)
    object = task
    users = 'Collaborateurs'

    if request.method == 'POST':
        user = User.objects.get(id=request.POST.get('user_id'))
        task.participants.add(user)
        return redirect('add_user', pk1=pk1, pk2=pk2)

    context = {'unread': unread(request), 'activity_msgs': Message.objects.all().order_by('-created')[0:10], 'task': task, 'project': project, 'object': object, 'users': users}
    if request.user == project.host:
        return render(request, 'base/user_list.html', context)
    else:
        return redirect('projects')
    


@login_required(login_url='login')
def project_chat(request, pk):
    project = Project.objects.get(id=pk)
    messages = project.message_set.all()
    users = 'Participants'

    if request.method == 'POST':    
        Message.objects.create(
            user = request.user,
            project = project,
            body = request.POST.get('body')
        )
        project.save()
        return redirect('project_chat', pk=pk)

    context = {'unread': unread(request), 
               'activity_msgs': Message.objects.all().order_by('-created')[0:10], 
               'project': project, 
               'object': project, 
               'users': users, 
               'messages': messages,
               'selected': 'C',
               }
    if request.user in project.participants.all():
        return render(request, 'base/project_chat.html', context)
    else:
        return redirect('projects')  
    

@login_required(login_url='login')
def profile(request, pk):
    user = User.objects.get(id=pk)
    profile = user.profile
    if user == request.user:
        selected = 'U'
    else:
        selected = None

    change_status = {
        'D': 'O',
        'O': 'C',
        'C': 'D',
    }

    if request.method == 'POST':
        status = request.POST.get('status')
        profile.status = change_status[status]
        profile.save()

        return redirect('profile', pk=pk)

    context = {'unread': unread(request), 
               'activity_msgs': Message.objects.all().order_by('-created')[0:10], 
               'user': user,
               'selected': selected
               }
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def update_profile(request, pk):
    user = User.objects.get(id=pk)
    profile_form = ProfileForm(instance=user.profile)
    user_form = UserForm(instance=user)

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=user.profile)
        user_form = UserForm(request.POST, instance=user)
        if profile_form.is_valid() and user_form.is_valid():
            user = user_form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            user.profile = profile_form.save()
            return redirect('profile', pk=user.id)

    context = {'unread': unread(request), 'activity_msgs': Message.objects.all().order_by('-created')[0:10], 'user_form': user_form, 'profile_form': profile_form}
    if request.user == user:
        return render(request, 'base/profile_form.html', context)
    else:
        return redirect('projects')
    

@login_required(login_url='login')
def invite_user(request, pk):
    project = Project.objects.get(id=pk)
    object = project
    users = 'Participants'
    invites = Invit.objects.all().filter(project=project)
    receivers = invites.values_list('receiver', flat=True).distinct()
    q = request.GET.get('q')
    if q:
        user_list = User.objects.all().filter(username__icontains=q)
    else:
        user_list = None

    if request.method == 'POST':
        user = User.objects.get(id=request.POST.get('user_id'))
        invite =Invit.objects.create(
            project=project,
            sender=request.user,
            receiver=user
        )
        notif = Notification.objects.create(
            invit=invite
        )
        notif.receivers.add(user)

        return redirect('invite_user', pk=pk)

    context = {'unread': unread(request), 'activity_msgs': Message.objects.all().order_by('-created')[0:10],
                'object': object, 
                'users': users,
                'project': project,
                'user_list': user_list,
                'receivers': receivers,
            }
    if request.user == project.host:
        return render(request, 'base/user_invite.html', context)
    else:
        return redirect('projects')
    

@login_required(login_url='login')
def notifications(request):
    notifications = Notification.objects.all().filter(receivers=request.user)
    for notification in notifications:
        notification.readers.add(request.user)  

    if request.method == 'POST':
        project = Project.objects.get(id=request.POST.get('project'))
        invite = Invit.objects.get(id=request.POST.get('invite'))
        invite.status = 'A'
        invite.save()
        project.participants.add(request.user)

        accepted = Notification.objects.create(
            invit=invite,
            title='A',
        )
        accepted.receivers.add(invite.sender)

        return redirect('notifications')

    context = {'unread': unread(request), 'activity_msgs': Message.objects.all().order_by('-created')[0:10],
                'notifications': notifications,

            }
    return render(request, 'base/notifications.html', context)
    

