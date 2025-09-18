# This file will define the URL endpoints for your API.
# DRF's routers can automatically generate a full set of
# URL patterns for a ViewSet, which simplifies things immensely.

from rest_framework.routers import DefaultRouter
from .views import *

app_name = 'api_admin'

router = DefaultRouter()
router.register(r'rounds', RoundViewSet, basename='round')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'suggested_groups', SuggestedGroupViewSet, basename='suggested_group')
router.register(r'project_preferences', ProjectPreferencesViewSet, basename='project_preference')
router.register(r'suggested_group_members', SuggestedGroupMemberViewSet, basename='suggested_group_member')
router.register(r'final_groups', FinalGroupViewSet, basename='final_group')
router.register(r'final_group_members', FinalGroupMemberViewSet, basename='final_group_member')
router.register(r'degrees', DegreeViewSet, basename='degrees')
router.register(r'majors', MajorViewSet, basename='majors')
urlpatterns = router.urls