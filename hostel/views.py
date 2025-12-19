from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Hostel, Student, Room
from .serializers import HostelSerializer, StudentSerializer, UpdateStudentSerializer, RoomSerializer

# Create your views here.
class HostelViewSet(ModelViewSet):
    queryset = Hostel.objects.select_related('address').all()
    serializer_class = HostelSerializer

class StudentViewSet(ModelViewSet):

    queryset = Student.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UpdateStudentSerializer
        return StudentSerializer 
    
class RoomViewSet(ModelViewSet):
    serializer_class = RoomSerializer

    def get_queryset(self):
        return Room.objects.filter(hostel=self.kwargs['hostel_pk']).all()
    
    def get_serializer_context(self):
        return {'hostel_id': self.kwargs['hostel_pk']}
    

