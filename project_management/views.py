from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from .models import User, Team, Project, Task, Comment, Setting, Integrer
from .forms import (
    ProjectForm,
    TaskForm,
    CommentForm,
    UserRegistrationForm,
    LoginForm,
    TeamForm,
    UserProfileForm,
    UserPasswordChangeForm,
    SettingsForm,
    UserPasswordResetForm,
    UserSetPasswordForm,
)


# Fonction pour vérifier si l'utilisateur est chef de projet
def is_chef_de_projet(user):
    return (
        user.groups.filter(name="Chef de projet").exists()
        or user.groups.filter(name="Administrateur").exists()
    )


# Décorateur pour les fonctions qui nécessitent le statut de chef de projet
def chef_projet_required(view_func):
    decorated_view = user_passes_test(is_chef_de_projet)(view_func)
    return decorated_view


# Vues d'authentification
def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte créé avec succès!")
            return redirect("project_management:home")
    else:
        form = UserRegistrationForm()
    return render(request, "project_management/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            print(user)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue, {user.username}!")
                next_url = request.GET.get("next", "project_management:home")
                return redirect(next_url)
            else:
                messages.error(request, "Identifiants invalides.")
    else:
        form = LoginForm()
    return render(request, "project_management/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect("project_management:login")


# Vue principale
@login_required
def home(request):
    # Récupérer toutes les tâches assignées à l'utilisateur
    user_tasks = Task.objects.filter(assigned_to=request.user).order_by("due_date")[:5]
    user_projects = Project.objects.filter(team__members=request.user).order_by(
        "-start_date"
    )[:5]

    # Toutes les tâches de l'utilisateur
    all_user_tasks = Task.objects.filter(assigned_to=request.user).order_by("due_date")

    # Compter les tâches en retard et terminées
    overdue_tasks_count = Task.objects.filter(
        assigned_to=request.user, due_date__lt=timezone.now()
    ).count()
    completed_tasks_count = Task.objects.filter(
        assigned_to=request.user, status="Terminé"
    ).count()

    group = request.user.groups.all()[0]

    context = {
        "user_tasks": user_tasks,
        "user_projects": user_projects,
        "all_user_tasks": all_user_tasks,  # Toutes les tâches pour affichage complet
        "group": group,
        "overdue_tasks_count": overdue_tasks_count,
        "completed_tasks_count": completed_tasks_count,
        "now": timezone.now(),  # Date et heure actuelles pour comparer avec les dates d'échéance
    }

    return render(request, "project_management/home.html", context)


# Vues de projets
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "project_management/project_list.html"
    context_object_name = "projects"
    paginate_by = 10  # Valeur par défaut

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrer par équipe si l'utilisateur n'est pas admin ou chef de projet
        if not is_chef_de_projet(self.request.user):
            queryset = Project.objects.filter(team__members=self.request.user)

        return queryset

    def get_paginate_by(self, queryset):
        # Obtenir les paramètres de pagination de l'utilisateur
        settings, created = Setting.objects.get_or_create(user=self.request.user)
        return settings.projects_per_page


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "project_management/project_detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        context["tasks"] = Task.objects.filter(project=project)
        context["comment_form"] = CommentForm()
        context["comments"] = Comment.objects.filter(project=project).order_by(
            "-publish_date"
        )
        return context


class ChefProjetRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_chef_de_projet(self.request.user)

    def handle_no_permission(self):
        messages.error(
            self.request,
            "Vous n'avez pas la permission d'effectuer cette action. Seuls les chefs de projet peuvent créer ou modifier des projets.",
        )
        return redirect("project_management:project_list")


class ProjectCreateView(LoginRequiredMixin, ChefProjetRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "project_management/project_form.html"
    success_url = reverse_lazy("project_management:project_list")

    def form_valid(self, form):
        messages.success(self.request, "Projet créé avec succès!")
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, ChefProjetRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "project_management/project_form.html"
    success_url = reverse_lazy("project_management:project_list")

    def form_valid(self, form):
        messages.success(self.request, "Projet mis à jour avec succès!")
        return super().form_valid(form)


class ProjectDeleteView(LoginRequiredMixin, ChefProjetRequiredMixin, DeleteView):
    model = Project
    template_name = "project_management/project_confirm_delete.html"
    success_url = reverse_lazy("project_management:project_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Projet supprimé avec succès!")
        return super().delete(request, *args, **kwargs)


# Vues de tâches
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "project_management/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrer par projet si spécifié
        project_id = self.request.GET.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        # Filtrer les tâches assignées à l'utilisateur s'il n'est pas admin ou chef de projet
        if not is_chef_de_projet(self.request.user):
            queryset = queryset.filter(assigned_to=self.request.user)

        return queryset


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "project_management/task_detail.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        context["comment_form"] = CommentForm()
        context["comments"] = Comment.objects.filter(task=task).order_by(
            "-publish_date"
        )
        return context


class TaskCreateView(LoginRequiredMixin, ChefProjetRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "project_management/task_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "project_management:project_detail", kwargs={"pk": self.object.project.pk}
        )

    def get_initial(self):
        initial = super().get_initial()
        if "project" in self.kwargs:
            initial["project"] = self.kwargs["project"]
        return initial

    def form_valid(self, form):
        messages.success(self.request, "Tâche créée avec succès!")
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "project_management/task_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "project_management:project_detail", kwargs={"pk": self.object.project.pk}
        )

    def form_valid(self, form):
        messages.success(self.request, "Tâche mise à jour avec succès!")
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, ChefProjetRequiredMixin, DeleteView):
    model = Task
    template_name = "project_management/task_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(
            "project_management:project_detail", kwargs={"pk": self.object.project.pk}
        )

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Tâche supprimée avec succès!")
        return super().delete(request, *args, **kwargs)


# Vue pour ajouter un commentaire
@login_required
def add_comment(request, type, pk):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user

            if type == "project":
                comment.project = get_object_or_404(Project, pk=pk)
                redirect_url = reverse_lazy(
                    "project_management:project_detail", kwargs={"pk": pk}
                )
            else:  # task
                comment.task = get_object_or_404(Task, pk=pk)
                redirect_url = reverse_lazy(
                    "project_management:task_detail", kwargs={"pk": pk}
                )

            comment.save()
            messages.success(request, "Commentaire ajouté avec succès!")
            return redirect(redirect_url)

    # En cas d'erreur, rediriger vers la page précédente
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
    return redirect("project_management:home")


# Users views
@login_required
def user_list(request):
    users = User.objects.all()

    # Obtenir les paramètres de pagination de l'utilisateur
    settings, created = Setting.objects.get_or_create(user=request.user)
    paginator = Paginator(users, settings.users_per_page)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "project_management/user_list.html",
        {
            "users": page_obj,
            "page_obj": page_obj,
            "is_paginated": True if paginator.num_pages > 1 else False,
        },
    )


def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    tasks = Task.objects.filter(assigned_to=user)
    teams = Team.objects.filter(integrer__user=user)
    return render(
        request,
        "project_management/user_detail.html",
        {"user": user, "tasks": tasks, "teams": teams},
    )


@login_required
def user_profile(request):
    """Vue pour afficher et modifier le profil de l'utilisateur connecté."""
    user = request.user
    tasks = Task.objects.filter(assigned_to=user)
    teams = Team.objects.filter(members=user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès!")
            return redirect("project_management:user_profile")
    else:
        form = UserProfileForm(instance=user)

    return render(
        request,
        "project_management/user_profile.html",
        {"user": user, "tasks": tasks, "teams": teams, "form": form},
    )


@login_required
def change_password(request):
    """Vue pour permettre à l'utilisateur de changer son mot de passe."""
    if request.method == "POST":
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Mettre à jour la session pour éviter la déconnexion
            update_session_auth_hash(request, user)
            messages.success(request, "Votre mot de passe a été modifié avec succès!")
            return redirect("project_management:user_profile")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = UserPasswordChangeForm(request.user)

    return render(request, "project_management/change_password.html", {"form": form})


@login_required
def user_settings(request):
    """Vue pour gérer les paramètres de pagination de l'utilisateur."""
    # Récupérer ou créer les paramètres pour l'utilisateur actuel
    settings, created = Setting.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = SettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Vos paramètres ont été mis à jour avec succès.")
            return redirect("project_management:user_settings")
    else:
        form = SettingsForm(instance=settings)

    return render(
        request,
        "project_management/user_settings.html",
        {"form": form, "title": "Paramètres de pagination"},
    )


# Vues pour la réinitialisation du mot de passe
def password_reset_request(request):
    if request.method == "POST":
        form = UserPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            associated_users = User.objects.filter(Q(email=email))

            for user in associated_users:
                # Générer le token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Construire le lien de réinitialisation
                reset_link = request.build_absolute_uri(
                    reverse(
                        "project_management:password_reset_confirm",
                        kwargs={"uidb64": uid, "token": token},
                    )
                )

                # Préparer l'email
                subject = "Demande de réinitialisation de mot de passe"
                message = render_to_string(
                    "project_management/password_reset_email.html",
                    {
                        "user": user,
                        "reset_link": reset_link,
                        "site_name": "Gestion de Projets - Mairie de Paris",
                    },
                )

                # Envoyer l'email
                try:
                    send_mail(subject, message, "noreply@mairie-paris.fr", [user.email])
                except BadHeaderError:
                    return HttpResponse("Entête invalide trouvé.")

                return redirect("project_management:password_reset_done")
    else:
        form = UserPasswordResetForm()

    return render(
        request=request,
        template_name="project_management/password_reset_form.html",
        context={"form": form},
    )


def password_reset_done(request):
    return render(
        request=request, template_name="project_management/password_reset_done.html"
    )


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = UserSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request, "Votre mot de passe a été réinitialisé avec succès!"
                )
                return redirect("project_management:password_reset_complete")
        else:
            form = UserSetPasswordForm(user)
        return render(
            request=request,
            template_name="project_management/password_reset_confirm.html",
            context={"form": form},
        )
    else:
        messages.error(request, "Le lien de réinitialisation est invalide ou a expiré.")
        return redirect("project_management:password_reset")


def password_reset_complete(request):
    return render(
        request=request, template_name="project_management/password_reset_complete.html"
    )


# Teams views
@login_required
def team_list(request):
    teams = Team.objects.all()

    # Obtenir les paramètres de pagination de l'utilisateur
    settings, created = Setting.objects.get_or_create(user=request.user)
    paginator = Paginator(teams, settings.teams_per_page)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "project_management/team_list.html",
        {
            "teams": page_obj,
            "page_obj": page_obj,
            "is_paginated": True if paginator.num_pages > 1 else False,
        },
    )


def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    users = User.objects.filter(integrer__team=team)
    projects = Project.objects.filter(team=team)
    return render(
        request,
        "project_management/team_detail.html",
        {"team": team, "users": users, "projects": projects},
    )


@login_required
@chef_projet_required
def team_create(request):
    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save()
            # Créer les entrées dans la table Integrer pour chaque membre
            for member in form.cleaned_data["members"]:
                Integrer.objects.create(user=member, team=team)
            messages.success(request, "Équipe créée avec succès!")
            return redirect("project_management:team_detail", team_id=team.id)
    else:
        form = TeamForm()

    return render(
        request,
        "project_management/team_form.html",
        {"form": form, "title": "Créer une équipe"},
    )


@login_required
@chef_projet_required
def team_update(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.method == "POST":
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            # Nettoyer les anciennes associations
            Integrer.objects.filter(team=team).delete()
            # Enregistrer l'équipe
            team = form.save()
            # Créer les nouvelles associations
            for member in form.cleaned_data["members"]:
                Integrer.objects.create(user=member, team=team)
            messages.success(request, "Équipe mise à jour avec succès!")
            return redirect("project_management:team_detail", team_id=team.id)
    else:
        form = TeamForm(instance=team)

    return render(
        request,
        "project_management/team_form.html",
        {"form": form, "title": "Modifier l'équipe"},
    )


@login_required
@chef_projet_required
def team_delete(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.method == "POST":
        team.delete()
        messages.success(request, "Équipe supprimée avec succès!")
        return redirect("project_management:team_list")

    return render(
        request, "project_management/team_confirm_delete.html", {"team": team}
    )
