from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Create your models here.


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=50,unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50)
    matricule = models.CharField(max_length=50, blank=True, null=True)
    last_login = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            # Créer les groupes s'ils n'existent pas
            admin_group, _ = Group.objects.get_or_create(name="Administrateur")
            chef_projet_group, _ = Group.objects.get_or_create(name="Chef de projet")
            membre_equipe_group, _ = Group.objects.get_or_create(name="Membre d'équipe")

            # Assigner l'utilisateur au groupe approprié basé sur son matricule
            if self.is_staff:
                self.groups.add(admin_group)
                self.role = "Administrateur"
            elif self.matricule and self.matricule.startswith("0045"):
                self.groups.add(chef_projet_group)
                self.role = "Chef de projet"
            else:
                self.groups.add(membre_equipe_group)
                self.role = "Membre d'équipe"
        super().save(*args, **kwargs)


class Team(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(User, related_name="teams")

    def __str__(self):
        return self.name


class Integrer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "team")


class Project(models.Model):
    STATUS_CHOICES = [
        ("En cours", "En cours"),
        ("Terminé", "Terminé"),
        ("Annulé", "Annulé"),
    ]

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="En cours")
    team = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, related_name="projects"
    )

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ("À faire", "À faire"),
        ("En cours", "En cours"),
        ("Terminé", "Terminé"),
    ]

    PRIORITY_CHOICES = [
        ("basse", "Basse"),
        ("moyenne", "Moyenne"),
        ("haute", "Haute"),
        ("urgente", "Urgente"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="a_faire")
    due_date = models.DateTimeField(blank=True, null=True)
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="moyenne"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField()
    publish_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments", null=True, blank=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Commentaire de {self.user.username} le {self.publish_date.strftime('%d/%m/%Y')}"


class Setting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    projects_per_page = models.IntegerField(default=10)
    users_per_page = models.IntegerField(default=10)
    teams_per_page = models.IntegerField(default=10)

    def __str__(self):
        return f"Paramètres de {self.user.username}"
