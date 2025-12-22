from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound
from .models import Hostel, Student, Room
from .serializers import HostelSerializer, StudentSerializer, UpdateStudentSerializer, RoomSerializer, RoomAssignmentSerializer
# Create your views here.
class HostelViewSet(ModelViewSet):
    queryset = Hostel.objects.select_related('address').all()
    serializer_class = HostelSerializer

class StudentViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    queryset = Student.objects.select_related('user').all()

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UpdateStudentSerializer
        return StudentSerializer 
    
class RoomViewSet(ModelViewSet):
    serializer_class = RoomSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None, hostel_pk=None):
        room = self.get_object()
        serializer = RoomAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.validated_data['student']
        if not room.is_available:
            return Response({'error': 'Room is full'}, status=status.HTTP_400_BAD_REQUEST)
        student.room = room
        student.save()
        return Response({"status": f"Assigned to Room {room.room_number}"})

    def get_queryset(self):
        if not Hostel.objects.filter(pk=self.kwargs['hostel_pk']).exists():
            raise NotFound('Hostel does not exist')
        return Room.objects.filter(hostel=self.kwargs['hostel_pk']).all()
    
    def get_serializer_context(self):
        return {'hostel_id': self.kwargs['hostel_pk']}
    

