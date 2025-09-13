# This file will define the URL endpoints for your API.
# DRF's routers can automatically generate a full set of
# URL patterns for a ViewSet, which simplifies things immensely.

from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'rounds', RoundViewSet, basename='rounds')
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'suggested_groups', SuggestedGroupViewSet, basename='suggested_groups')
urlpatterns = router.urls