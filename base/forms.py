from django.forms import ModelForm, CharField, PasswordInput, ValidationError, DateInput
from django.contrib.auth.forms import UserCreationForm
from .models import User, Project, Task, Profile

class LoginForm(ModelForm):
    password = CharField(label='Mot de passe', widget=PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password']
        labels = {
            'email': 'Adresse email',
        }

class RegisterForm(UserCreationForm):
    password1 = CharField(label='Mot de passe', widget=PasswordInput)
    password2 = CharField(label='Confirmer le mot de passe', widget=PasswordInput)

    class Meta():
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        labels = {
            'first_name': "Prénom", 
            'last_name': "Nom", 
            'username': "Nom d'utilisateur", 
            'email': "Adresse email",
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("email")
        return email
    

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        exclude = ['host', 'participants', 'pourcentage']
        labels = {
            'title': 'Titre',
            'attachment': 'Fichier',
            'deadline': 'Date limite',
        }
        widgets = {
            'deadline': DateInput(attrs={'placeholder': 'AAAA-MM-JJ'}),
        }


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline']
        labels = {
            'title': 'Titre', 
            'deadline': 'Date limite'
        }
        widgets = {
            'deadline': DateInput(attrs={'placeholder': 'AAAA-MM-JJ'}),
        }


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username']
        labels = {'username': "Nom d'utilisateur"}


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'profil', 'competences']
        labels = {'avatar': "changer la photo de profile",
                  'profil': 'profile',
                  'competences': 'compétences',
                }
