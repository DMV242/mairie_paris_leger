from django.contrib import admin
from django.utils.html import format_html
from .models import User, Team, Project, Task, Comment, Setting, Integrer


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role_colored", "matricule", "last_login")
    search_fields = ("username", "email", "matricule")
    list_filter = ("role", "is_staff", "is_active")
    readonly_fields = ("last_login",)
    fieldsets = (
        ("Informations personnelles", {
            "fields": ("username", "email", "matricule", "role")
        }),
        ("Autorisations", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            "classes": ("collapse",)
        }),
        ("Dates importantes", {
            "fields": ("last_login", "date_joined"),
            "classes": ("collapse",)
        }),
    )

    def role_colored(self, obj):
        colors = {
            "Administrateur": "#BF0A30",
            "Chef de projet": "#1E3A8A",
            "Membre d'équipe": "#2E7D32"
        }
        color = colors.get(obj.role, "#333333")
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.role)
    role_colored.short_description = "Rôle"

    actions = ["make_admin", "make_project_manager", "make_team_member"]

    def make_admin(self, request, queryset):
        queryset.update(role="Administrateur", is_staff=True)
    make_admin.short_description = "Définir comme administrateur"

    def make_project_manager(self, request, queryset):
        queryset.update(role="Chef de projet", is_staff=False)
    make_project_manager.short_description = "Définir comme chef de projet"

    def make_team_member(self, request, queryset):
        queryset.update(role="Membre d'équipe", is_staff=False)
    make_team_member.short_description = "Définir comme membre d'équipe"


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "members_count")
    search_fields = ("name",)
    filter_horizontal = ("members",)

    def members_count(self, obj):
        count = obj.members.count()
        return format_html('<span style="font-weight: bold;">{}</span> membre(s)', count)
    members_count.short_description = "Membres"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "team", "start_date", "end_date", "status_colored", "tasks_count")
    list_filter = ("status", "team")
    search_fields = ("name", "description")
    date_hierarchy = "start_date"

    def status_colored(self, obj):
        colors = {
            "En cours": "#1976D2",
            "Terminé": "#2E7D32",
            "Annulé": "#BF0A30"
        }
        color = colors.get(obj.status, "#333333")
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.status)
    status_colored.short_description = "Statut"

    def tasks_count(self, obj):
        return obj.tasks.count()
    tasks_count.short_description = "Tâches"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "assigned_to", "due_date", "status_colored", "priority_colored")
    list_filter = ("status", "priority", "project")
    search_fields = ("title", "description")
    date_hierarchy = "due_date"

    def status_colored(self, obj):
        colors = {
            "En cours": "#1976D2",
            "Terminé": "#2E7D32",
            "À faire": "#F57C00"
        }
        color = colors.get(obj.status, "#333333")
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.status)
    status_colored.short_description = "Statut"

    def priority_colored(self, obj):
        colors = {
            "haute": "#BF0A30",
            "moyenne": "#F57C00",
            "basse": "#2E7D32",
            "urgente": "#D32F2F"
        }
        color = colors.get(obj.priority, "#333333")
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.priority)
    priority_colored.short_description = "Priorité"

    actions = ["mark_as_in_progress", "mark_as_completed"]

    def mark_as_in_progress(self, request, queryset):
        queryset.update(status="En cours")
    mark_as_in_progress.short_description = "Marquer comme en cours"

    def mark_as_completed(self, request, queryset):
        queryset.update(status="Terminé")
    mark_as_completed.short_description = "Marquer comme terminé"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "short_content", "publish_date", "related_to")
    list_filter = ("publish_date", "user")
    search_fields = ("content",)
    date_hierarchy = "publish_date"

    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    short_content.short_description = "Contenu"

    def related_to(self, obj):
        if obj.task:
            return format_html('Tâche: <a href="{}">{}</a>',
                f"/admin/project_management/task/{obj.task.id}/change/",
                obj.task.title)
        elif obj.project:
            return format_html('Projet: <a href="{}">{}</a>',
                f"/admin/project_management/project/{obj.project.id}/change/",
                obj.project.name)
        return "—"
    related_to.short_description = "Lié à"


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "projects_per_page",
        "users_per_page",
        "teams_per_page",
    )


@admin.register(Integrer)
class IntegrerAdmin(admin.ModelAdmin):
    list_display = ("user", "team")
    list_filter = ("team",)

# Personnalisation du site d'administration
admin.site.site_header = "Administration Mairie de Paris"
admin.site.site_title = "Gestion de Projets"
admin.site.index_title = "Tableau de bord"
