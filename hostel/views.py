from datetime import date
from django.db.models import Count 
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .permissions import IsOwnerOrAdmin
from .models import (
    Fee,
    Hostel, 
    HostelManager,
    Student, 
    RoomAssignment, 
    RoomPricing,
    Room, 
    Payment
)
from .serializers import (
    FeeSerializer,
    HostelSerializer, 
    HostelManagerSerializer,
    StudentSerializer, 
    UpdateStudentSerializer, 
    RoomAssignmentSerializer,
    RoomSerializer,
    PaymentSerializer
)
# Create your views here.
class HostelViewSet(ModelViewSet):
    queryset = Hostel.objects.select_related('address').all()
    serializer_class = HostelSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

class StudentViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    queryset = Student.objects.select_related('user').all()
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_permissions(self):
        if self.action in ['list']:
            permission_classes = [IsAdminUser]
        elif self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]
        
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UpdateStudentSerializer
        return StudentSerializer 
    
class RoomViewSet(ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if not Hostel.objects.filter(pk=self.kwargs['hostel_pk']).exists():
            raise NotFound('Rooms do not exist')
        
        return Room.objects.select_related('hostel').\
                    annotate(student_count=Count('room_assignment')).\
                    filter(hostel=self.kwargs['hostel_pk'])
    
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

class PaymentViewSet(ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def verify(self, request):
        reference = request.data.get('reference')
        fee_id = request.data.get('fee_id')

        if not reference:
            return  Response({'error': "No reference provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        if Payment.objects.filter(reference=reference).exists():
            return Response({'error': "Payment already processed"}, status=status.HTTP_400_BAD_REQUEST)
        
        

    def  get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Payment.objects.all()
        
        if hasattr(user, 'student'):
            return Payment.objects.filter(student=user.student)
        
        return Payment.objects.none()

class FeeViewSet(ModelViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer
    permission_classes = [IsAdminUser]


class HostelManagerViewSet(ModelViewSet):
    queryset = HostelManager.objects.select_related('hostel', 'user').all()
    permission_classes = [IsAdminUser]
    serializer_class = HostelManagerSerializer

