# This file will define the URL endpoints for your API.
# DRF's routers can automatically generate a full set of
# URL patterns for a ViewSet, which simplifies things immensely.

from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'rounds', RoundViewSet, basename='rounds')
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'suggested_groups', SuggestedGroupViewSet, basename='suggested_groups')
router.register(r'project_preferences', ProjectPreferencesViewSet, basename='project_preferences')
router.register(r'suggested_group_member', SuggestedGroupMemberViewSet, basename='suggested_group_member')
router.register(r'final_groups', FinalGroupViewSet, basename='final_groups')
router.register(r'final_group_member', FinalGroupMemberViewSet, basename='final_group_member')
router.register(r'degrees', DegreeViewSet, basename='degrees')
router.register(r'majors', MajorViewSet, basename='majors')
urlpatterns = router.urls