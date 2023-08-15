from django.contrib import admin
from .models import Profile, Project, Task, Notification, Invit, Message

# Register your models here.
admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Notification)
admin.site.register(Invit)
admin.site.register(Message)