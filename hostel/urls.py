from rest_framework.routers import DefaultRouter
from .views import HostelViewSet, StudentViewSet

router = DefaultRouter()
router.register('hostels', HostelViewSet, basename='hostel')
router.register('students', StudentViewSet, basename='students')

urlpatterns = router.urls
