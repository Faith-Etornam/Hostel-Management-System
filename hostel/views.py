from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Hostel
from .serializers import HostelSerializer

# Create your views here.
class HostelViewSet(ModelViewSet):
    queryset = Hostel.objects.all()
    serializer_class = HostelSerializer
    
