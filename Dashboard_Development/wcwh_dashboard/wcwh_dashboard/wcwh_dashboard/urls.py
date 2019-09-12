from django.contrib import admin
from django.urls import include, path

urlpatterns = [
	path('feedback/',include('feedback.urls')),
	path('admin/',admin.site.urls),
]