from django.contrib import admin
from django.urls import path, include
from accounts import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.upload_ppt, name='upload_ppt'),
    path('entry/', views.entry, name='entry'),
    path('signup/', views.signup, name='signup'),
    path('past/', views.view_past_ppts, name='past'),
    path('login/', views.login, name='login'),
    path('signup.html', views.signup, name='signup_html'),
    path('signup.html', views.login, name='login_html'),
    path('download/<str:presentation_id>/', views.download_presentation, name='download_presentation'),

    # Other URLs
]
#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
