from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Hostel, Student
from .serializers import HostelSerializer, StudentSerializer

# Create your views here.
class HostelViewSet(ModelViewSet):
    queryset = Hostel.objects.select_related('address').all()
    serializer_class = HostelSerializer

class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

