from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q

from .models import User, Team, Project, Task, Comment
from .serializers import (
    UserSerializer, TeamSerializer, TeamDetailSerializer,
    ProjectSerializer, ProjectDetailSerializer,
    TaskSerializer, TaskDetailSerializer,
    CommentSerializer,  UserLoginSerializer
)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():


        matricule = serializer.validated_data.get('matricule')
        password = serializer.validated_data.get('password')

        user = User.objects.get(matricule=matricule)

        if user.check_password(password):
            refresh = RefreshToken.for_user(user)

            user_serializer = UserSerializer(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)

        return Response({'detail': 'Identifiants invalides'}, status=status.HTTP_401_UNAUTHORIZED)





    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        print(self.request.headers)
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer

    def get_queryset(self):
        queryset = self.queryset


        status_param = self.request.query_params.get('status', None)
        team_param = self.request.query_params.get('team', None)
        search_param = self.request.query_params.get('search', None)

        if status_param:
            queryset = queryset.filter(status=status_param)

        if team_param:
            queryset = queryset.filter(team__id=team_param)

        if search_param:
            queryset = queryset.filter(
                Q(name__icontains=search_param) |
                Q(description__icontains=search_param)
            )

        return queryset

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskSerializer

    def get_queryset(self):
        queryset = self.queryset
        project_param = self.request.query_params.get('project', None)
        status_param = self.request.query_params.get('status', None)
        priority_param = self.request.query_params.get('priority', None)
        user_param = self.request.query_params.get('user', None)
        upcoming_param = self.request.query_params.get('upcoming', None)

        if project_param:
            queryset = queryset.filter(project__id=project_param)

        if status_param:
            queryset = queryset.filter(status=status_param)

        if priority_param:
            queryset = queryset.filter(priority=priority_param)

        if user_param:
            queryset = queryset.filter(assigned_to__id=user_param)

        if upcoming_param and upcoming_param.lower() == 'true':
            from django.utils import timezone
            import datetime
            seven_days_later = timezone.now() + datetime.timedelta(days=7)
            queryset = queryset.filter(
                due_date__gte=timezone.now(),
                due_date__lte=seven_days_later
            )

        return queryset

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TeamDetailSerializer
        return TeamSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = self.queryset
        role_param = self.request.query_params.get('role', None)
        team_param = self.request.query_params.get('team', None)

        if role_param:
            queryset = queryset.filter(role=role_param)

        if team_param:
            queryset = queryset.filter(teams__id=team_param)

        return queryset

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_api(request):
    """
    Vue API pour récupérer le profil de l'utilisateur connecté
    """
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)

class CommentListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommentSerializer

    def get_queryset(self):
        project_id = self.request.query_params.get('project', None)
        task_id = self.request.query_params.get('task', None)

        if project_id:
            return Comment.objects.filter(project__id=project_id).order_by('-publish_date')
        elif task_id:
            return Comment.objects.filter(task__id=task_id).order_by('-publish_date')

        return Comment.objects.none()