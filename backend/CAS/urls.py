"""
URL configuration for CAS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.urls import path, include
from django.conf.urls.static import static 
from django.http import HttpResponse

from admin_app import views as admin_views


urlpatterns = [
    path('login/login_success.html/', admin_views.login_success, name='login_success'),
    path('admin/', admin.site.urls),
    path('login/', admin_views.login_view, name='login'),
    path('api/students/', include('student_app.urls')),
    path('api/projects/', include('project_app.urls')),
    path('api/admins/', include('admin_app.urls')),
    path('test/', admin_views.test_view, name='test'),
    # Root URL view
    path('', lambda request: HttpResponse("Welcome to CAS API!")),
]

# During development, add URL path to serve resume & CV files. 
# Map /media/ URL to the media/ folder on disk 
#if settings.DEBUG: 
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
