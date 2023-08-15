from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Create your models here.
class Profile(models.Model):
    user_status = [('D', 'Disponible'), ('O', 'Occuper'), ('C', 'Congé')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profil = models.CharField(max_length=100, null=True, blank=True)
    competences = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=user_status, default='D')
    avatar = models.ImageField(null=True, default='avatar.png')

    
class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    attachment = models.FileField(null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    deadline = models.DateField(null=True, blank=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    participants = models.ManyToManyField(User, related_name='project_participants', blank=True)
    pourcentage = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk:
            if self.task_set.exists():
                self.pourcentage = round((self.task_set.filter(status='T').count() / self.task_set.all().count()) * 100)
            else:
                self.pourcentage = 0
        else:
            self.pourcentage = 0
        super(Project, self).save(*args, **kwargs)

    class Meta():
        ordering = ['-updated', '-created']


class Task(models.Model):
    status_choices = [('A', 'En attente'), ('C', 'En cours'), ('T', 'Terminé')]

    status = models.CharField(max_length=1, choices=status_choices, default='A')
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    deadline = models.DateField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    participants = models.ManyToManyField(User, related_name='task_participants', blank=True)

    def __str__(self):
        if self.description:
            if len(self.description) > 101:
                return self.description[0:100]+'...'
            else:
                return self.description
        return ''

    def clean(self):
        if self.deadline:
            if self.deadline > self.project.deadline:
                raise ValidationError(
                    {'deadline':_(
                        "la date limite de la tache doit être plus proche que la date limite du projet."
                    )}
                )
        
    def save(self, *args, **kwargs):
        super(Task, self).save(*args, **kwargs)
        self.project.save()
    

class Message(models.Model):
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        if len(self.body) > 51:
            return self.body[0:50]+'...'
        else:
            return self.body


class Invit(models.Model):
    status_choices = [('P', 'Pending'), ('A', 'Accepted')]

    status = models.CharField(max_length=1, choices=status_choices, default='P')
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='invit_sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='invit_receiver')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Notification(models.Model):
    status_choices = [('P', 'Pending'), ('S', 'Seen')]

    title = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=1, choices=status_choices, default='P')
    created = models.DateTimeField(auto_now_add=True)   
    receivers = models.ManyToManyField(User)
    readers = models.ManyToManyField(User, related_name='readers')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    invit = models.ForeignKey(Invit, on_delete=models.CASCADE, null=True)

    class Meta():
        ordering = ['-created']
