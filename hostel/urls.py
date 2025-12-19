from rest_framework.routers import DefaultRouter
from .views import HostelViewSet, StudentViewSet, RoomViewSet

router = DefaultRouter()
router.register('hostels', HostelViewSet, basename='hostel')
router.register('students', StudentViewSet, basename='students')
router.register('rooms', RoomViewSet, basename='rooms')

urlpatterns = router.urls
