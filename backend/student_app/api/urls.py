from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, ProjectViewSet, MajorViewSet, StudentApplicationView, RoundViewSet

app_name = 'api_student'

router = DefaultRouter()

router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'majors', MajorViewSet, basename='major')
router.register(r'rounds', RoundViewSet, basename='round')

urlpatterns = [
    # Path for the form submission API
    path('submitApplication/', StudentApplicationView.as_view(), name="form_submission"),
]
# Add the router's URLs to the list
urlpatterns += router.urls
