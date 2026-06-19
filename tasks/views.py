from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Task, TaskComment
from .serializers import (
    TaskListSerializer, TaskDetailSerializer,
    TaskCreateSerializer, TaskCommentSerializer
)
from core.permissions import (
    IsAuthenticatedInTenant, HasPermission, FeatureRequired, user_has_permission,
)
from notifications.utils import notify

FEATURE = FeatureRequired("tasks_module")

TASK_PATCH_ALLOWED = {
    "title", "description", "priority", "status",
    "department", "assigned_to", "due_date", "notes",
}


class TaskListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("tasks.create")()]
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("tasks.view")()]

    def get(self, request):
        qs = Task.objects.filter(
            tenant=request.user.tenant,
            is_archived=False
        ).select_related("assigned_to", "assigned_by")

        status_f   = request.query_params.get("status")
        priority_f = request.query_params.get("priority")
        dept_f     = request.query_params.get("department")

        if status_f:   qs = qs.filter(status=status_f)
        if priority_f: qs = qs.filter(priority=priority_f)
        if dept_f:     qs = qs.filter(department=dept_f)

        if not (request.user.is_super_admin or user_has_permission(request.user, "tasks.view_all")):
            qs = qs.filter(assigned_to=request.user)

        return Response(TaskListSerializer(qs, many=True).data)

    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(TaskDetailSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("tasks.delete")()]
        if self.request.method == "PATCH":
            return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("tasks.edit")()]
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("tasks.view")()]

    def _get_task(self, pk, user):
        return get_object_or_404(Task, pk=pk, tenant=user.tenant, is_archived=False)

    def get(self, request, pk):
        return Response(TaskDetailSerializer(self._get_task(pk, request.user)).data)

    def patch(self, request, pk):
        task      = self._get_task(pk, request.user)
        safe_data = {k: v for k, v in request.data.items() if k in TASK_PATCH_ALLOWED}
        serializer = TaskCreateSerializer(
            task, data=safe_data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        if safe_data.get("status") == "completed" and not task.completed_at:
            task.completed_at = timezone.now()
            task.save()
        return Response(TaskDetailSerializer(task).data)

    def delete(self, request, pk):
        task = self._get_task(pk, request.user)
        task.is_archived = True
        task.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskCommentView(APIView):
    def get_permissions(self):
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("tasks.view")()]

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, tenant=request.user.tenant, is_archived=False)
        comment = TaskComment.objects.create(
            task       = task,
            comment    = request.data.get("comment", ""),
            created_by = request.user
        )
        return Response(TaskCommentSerializer(comment).data, status=status.HTTP_201_CREATED)