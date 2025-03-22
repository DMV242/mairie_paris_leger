from django.urls import path
from . import views

app_name = "project_management"

urlpatterns = [
    # Authentification
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Mot de passe oublié
    path("password-reset/", views.password_reset_request, name="password_reset"),
    path("password-reset/sent/", views.password_reset_done, name="password_reset_done"),
    path(
        "password-reset/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        views.password_reset_complete,
        name="password_reset_complete",
    ),
    # Page d'accueil
    path("", views.home, name="home"),
    # Projets
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path("projects/create/", views.ProjectCreateView.as_view(), name="project_create"),
    path(
        "projects/<int:pk>/", views.ProjectDetailView.as_view(), name="project_detail"
    ),
    path(
        "projects/<int:pk>/update/",
        views.ProjectUpdateView.as_view(),
        name="project_update",
    ),
    path(
        "projects/<int:pk>/delete/",
        views.ProjectDeleteView.as_view(),
        name="project_delete",
    ),
    # Tâches
    path("tasks/", views.TaskListView.as_view(), name="task_list"),
    path(
        "projects/<int:project>/tasks/create/",
        views.TaskCreateView.as_view(),
        name="task_create",
    ),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="task_detail"),
    path("tasks/<int:pk>/update/", views.TaskUpdateView.as_view(), name="task_update"),
    path("tasks/<int:pk>/delete/", views.TaskDeleteView.as_view(), name="task_delete"),
    # Commentaires
    path(
        "projects/<int:pk>/comment/",
        views.add_comment,
        {"type": "project"},
        name="project_comment",
    ),
    path(
        "tasks/<int:pk>/comment/",
        views.add_comment,
        {"type": "task"},
        name="task_comment",
    ),
    # Utilisateurs
    path("users/", views.user_list, name="user_list"),
    path("users/<int:user_id>/", views.user_detail, name="user_detail"),
    path("profile/", views.user_profile, name="user_profile"),
    path("profile/change-password/", views.change_password, name="change_password"),
    path("settings/", views.user_settings, name="user_settings"),
    # Équipes
    path("teams/", views.team_list, name="team_list"),
    path("teams/<int:team_id>/", views.team_detail, name="team_detail"),
    path("teams/create/", views.team_create, name="team_create"),
    path("teams/<int:team_id>/update/", views.team_update, name="team_update"),
    path("teams/<int:team_id>/delete/", views.team_delete, name="team_delete"),
]
