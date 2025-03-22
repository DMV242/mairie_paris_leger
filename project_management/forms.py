from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth import get_user_model
from .models import Project, Task, Comment, Team, Setting
from django.db.models import Q

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    matricule = forms.CharField(
        max_length=50,
        required=False,
        help_text="Toutes usurpations de Matricule seront sanctionnées !!.",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "matricule",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les messages d'aide
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full sm:text-sm border-gray-300 rounded-lg"
                }
            )


class UserProfileForm(forms.ModelForm):
    """Formulaire pour mettre à jour le profil utilisateur."""

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "matricule"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les messages d'aide
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full sm:text-sm border-gray-300 rounded-lg"
                }
            )

        # Ajouter des placeholders
        self.fields["username"].widget.attrs["placeholder"] = "Nom d'utilisateur"
        self.fields["email"].widget.attrs["placeholder"] = "Email"
        self.fields["first_name"].widget.attrs["placeholder"] = "Prénom"
        self.fields["last_name"].widget.attrs["placeholder"] = "Nom"
        self.fields["matricule"].widget.attrs["placeholder"] = "Matricule (optionnel)"
        self.fields["matricule"].required = False


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full sm:text-sm border-gray-300 rounded-lg",
                "placeholder": "Nom d'utilisateur",
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full sm:text-sm border-gray-300 rounded-lg",
                "placeholder": "Mot de passe",
            }
        )
    )


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "start_date",
            "end_date",
            "status",
            "team",
        ]
        widgets = {
            "start_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
        team = forms.ModelChoiceField(queryset=Team.objects.all())
        status = forms.ChoiceField(choices=Project.STATUS_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des classes CSS aux widgets
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full sm:text-sm border-gray-300 rounded-lg"
                }
            )


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "due_date",
            "priority",
            "assigned_to",
            "project",
        ]
        widgets = {
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des classes CSS aux widgets
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full sm:text-sm border-gray-300 rounded-lg"
                }
            )
        try:
            # Filtrer les utilisateurs pour n'afficher que les membres de l'équipe du projet
            if self.instance and self.instance.project and self.instance.project.team:
                self.fields["assigned_to"].queryset = (
                    self.instance.project.team.members.all()
                )
            else:
                self.fields["assigned_to"].queryset = User.objects.none()
        except Exception as e:
            self.fields["assigned_to"].queryset = User.objects.filter(
                groups__name__in=["Membre d'équipe", "Chef de projet"]
            )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full sm:text-sm border-gray-300 rounded-lg",
                    "placeholder": "Ajouter un commentaire...",
                }
            ),
        }


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "members"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full sm:text-sm border-gray-300 rounded-lg",
                    "placeholder": "Nom de l'équipe",
                }
            ),
            "members": forms.SelectMultiple(
                attrs={
                    "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full sm:text-sm border-gray-300 rounded-lg",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les utilisateurs pour n'afficher que ceux qui sont membres d'équipe ou chef de projet
        self.fields["members"].queryset = User.objects.filter(
            groups__name__in=["Membre d'équipe", "Chef de projet"]
        )
        self.fields["members"].label = "Membres de l'équipe"


class UserPasswordChangeForm(PasswordChangeForm):
    """Formulaire pour changer le mot de passe."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les champs
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full px-4 py-3 text-base border-gray-300 rounded-lg"
                }
            )

        # Ajouter des placeholders et labels plus clairs
        self.fields["old_password"].widget.attrs[
            "placeholder"
        ] = "Votre mot de passe actuel"
        self.fields["old_password"].label = "Mot de passe actuel"

        self.fields["new_password1"].widget.attrs[
            "placeholder"
        ] = "Votre nouveau mot de passe"
        self.fields["new_password1"].label = "Nouveau mot de passe"

        self.fields["new_password2"].widget.attrs[
            "placeholder"
        ] = "Confirmer votre nouveau mot de passe"
        self.fields["new_password2"].label = "Confirmation du nouveau mot de passe"


class SettingsForm(forms.ModelForm):
    """Formulaire pour gérer les paramètres de pagination."""

    class Meta:
        model = Setting
        fields = ["projects_per_page", "users_per_page", "teams_per_page"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les champs
        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {
                    "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full sm:text-sm border-gray-300 rounded-lg",
                    "min": "5",
                    "max": "50",
                    "type": "number",
                }
            )

        # Labels plus descriptifs
        self.fields["projects_per_page"].label = "Projets par page"
        self.fields["projects_per_page"].help_text = (
            "Nombre de projets affichés par page (5-50)"
        )

        self.fields["users_per_page"].label = "Utilisateurs par page"
        self.fields["users_per_page"].help_text = (
            "Nombre d'utilisateurs affichés par page (5-50)"
        )

        self.fields["teams_per_page"].label = "Équipes par page"
        self.fields["teams_per_page"].help_text = (
            "Nombre d'équipes affichées par page (5-50)"
        )


class UserPasswordResetForm(PasswordResetForm):
    """Formulaire pour réinitialiser le mot de passe."""

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full sm:text-sm border-gray-300 rounded-lg",
                "placeholder": "Entrez votre adresse email",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Aucun compte n'est associé à cette adresse email."
            )
        return email


class UserSetPasswordForm(SetPasswordForm):
    """Formulaire pour définir un nouveau mot de passe."""

    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(
            attrs={
                "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full sm:text-sm border-gray-300 rounded-lg",
                "placeholder": "Entrez votre nouveau mot de passe",
            }
        ),
    )

    new_password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(
            attrs={
                "class": "shadow-sm focus:ring-fr-blue focus:border-fr-blue block w-full sm:text-sm border-gray-300 rounded-lg",
                "placeholder": "Confirmez votre nouveau mot de passe",
            }
        ),
    )
