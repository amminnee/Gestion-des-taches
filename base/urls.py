from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.login_user, name="login"),
    path("projects/", views.projects, name='projects'),
    path("register/", views.register_user, name="register"),
    path("logout/", views.logout_user, name="logout"),
    path("my-tasks/", views.tasks, name="tasks"),
    path("notifications/", views.notifications, name="notifications"),


    path("create-project/", views.create_project, name="create_project"),
    path("update-prject/<str:pk>/", views.update_project, name="update_project"),
    path("delete-project/<str:pk>/", views.delete_project, name="delete_project"),

    path("project/<str:pk>/tasks/", views.project_tasks, name="project_tasks"),
    path("project/<str:pk>/description/", views.project_description, name="project_description"),
    path("project/<str:pk>/chat/", views.project_chat, name="project_chat"),
    
    path("project/<str:pk>/create-task/", views.create_task, name="create_task"),
    path("project/<str:pk1>/update-task/<str:pk2>/", views.update_task, name="update_task"),

    path("project/<str:pk1>/task-description/<str:pk2>/", views.task_description, name="task_description"),
    path("project/<str:pk1>/delete-task/<str:pk2>/", views.delete_task, name="delete_task"),
    path("project/<str:pk1>/task/<str:pk2>/add-user/", views.add_user, name="add_user"),
    path("project/<str:pk>/invite-user/", views.invite_user, name="invite_user"),


    path("user-profile/<str:pk>/", views.profile, name="profile"),
    path("update-profile/<str:pk>/", views.update_profile, name="update_profile"),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)