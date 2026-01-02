from rest_framework_nested import routers
from .views import (
    FeeViewSet,
    HostelViewSet, 
    HostelManagerViewSet,
    StudentViewSet, 
    RoomViewSet,
    RoomPricingViewSet,
    PaymentViewSet,
)

router = routers.DefaultRouter()

router.register('hostels', HostelViewSet, basename='hostel')
router.register('students', StudentViewSet, basename='students')
router.register('payments', PaymentViewSet, basename='payments')
router.register('fees', FeeViewSet, basename='fees')
router.register('hostel_managers', HostelManagerViewSet, basename='managers')
router.register('room_pricing',RoomPricingViewSet, basename='room_pricing' )

room_router = routers.NestedDefaultRouter(router, 'hostels', lookup='hostel')
room_router.register('rooms', RoomViewSet, basename='hostel-rooms')

urlpatterns = router.urls + room_router.urls
