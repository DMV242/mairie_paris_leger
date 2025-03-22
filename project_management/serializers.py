from rest_framework import serializers
from .models import User, Team, Project, Task, Comment, Integrer, Setting

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'matricule', 'last_login']

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name']

class TeamDetailSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'members']

class ProjectSerializer(serializers.ModelSerializer):
    team_name = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'status', 'team', 'team_name']

    def get_team_name(self, obj):
        return obj.team.name if obj.team else None

class ProjectDetailSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'status', 'team']

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'due_date', 'priority','assigned_to', 'assigned_to_name', 'project', 'project_name', 'created_at']

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.username if obj.assigned_to else None

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None

class TaskDetailSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'due_date', 'priority','assigned_to', 'project', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'publish_date', 'user', 'user_name', 'task', 'project']

    def get_user_name(self, obj):
        return obj.user.username if obj.user else None

class LoginSerializer(serializers.Serializer):
    matricule = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=128, write_only=True)

class UserLoginSerializer(serializers.Serializer):
    matricule = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        fields = ['matricule', 'password']