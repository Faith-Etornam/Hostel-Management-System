from datetime import date
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound
from .models import Hostel, Student, Room, RoomAssignment, RoomPricing
from django.db.models import Count
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

    def get_queryset(self):
        if not Hostel.objects.filter(pk=self.kwargs['hostel_pk']).exists():
            raise NotFound('Hostel does not exist')
        return Room.objects.select_related('hostel').filter(hostel=self.kwargs['hostel_pk'])
    
    def get_serializer_context(self):
        context = super().get_serializer_context()

        if 'hostel_pk' in self.kwargs:
            hostel_id = self.kwargs['hostel_pk']

            prices = RoomPricing.objects.filter(hostel=hostel_id)
            price_map = {p.capacity: p.price for p in prices}
        
            context['price_map'] = price_map
            context['hostel_id'] = hostel_id

        return context
    
    def get_serializer_class(self):
        if self.action == 'assign':
            return RoomAssignmentSerializer
        return super().get_serializer_class()
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None, hostel_pk=None):
        room = self.get_object()
        serializer = RoomAssignmentSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            student = serializer.validated_data['student']

        if not room.is_available:
            return Response({'error': 'Room is full'}, status=status.HTTP_400_BAD_REQUEST)
        student.room = room
        student.save()

        current_year = date.today().year + 1
        
        start_date = date(current_year, 1, 20) 
        
        end_date = date(current_year, 9, 30)

        RoomAssignment.objects.create(room=room, student=student, start_date=start_date, end_date=end_date)

        return Response({"status": f"Assigned to Room {room.room_number}"})

    

