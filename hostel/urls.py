from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import HostelViewSet, StudentViewSet, RoomViewSet

router = routers.DefaultRouter()
router.register('hostels', HostelViewSet, basename='hostel')
router.register('students', StudentViewSet, basename='students')

room_router = routers.NestedDefaultRouter(router, 'hostels', lookup='hostel')
room_router.register('room', RoomViewSet, basename='rooms')

urlpatterns = router.urls + room_router.urls
