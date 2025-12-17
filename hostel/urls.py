from rest_framework.routers import DefaultRouter
from .views import HostelViewSet

router = DefaultRouter()
router.register('hostels', HostelViewSet, basename='hostel')

urlpatterns = router.urls
