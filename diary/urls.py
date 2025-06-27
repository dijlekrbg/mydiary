from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from .views.api import UserRegisterAPIView, EntriesByDayAPIView
from .views.frontend import photo_gallery, photo_delete, async_hello
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .views.frontend import (home, diary_list, diary_create, diary_edit, diary_delete, diary_search,register_view, login_view, logout_view,dashboard, calendar_view, entries_by_day)
from .views.frontend import archive_entry, unarchive_entry, archived_entries, profile_update, diary_pdf
from .views.api import (DiaryEntryListCreateAPIView, DiaryEntryDetailAPI, DiaryEntryViewSet, CalendarEventsAPIView , get_token)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = DefaultRouter()
router.register(r'api/v1/diary', DiaryEntryViewSet, basename='diaryentry')


schema_view = get_schema_view(
    openapi.Info(
        title="Günlük API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', home, name='home'),
    path('',include(router.urls)),
    path('diary/',diary_list, name='diary_list'),
    path('diary/new/', diary_create, name='diary_create'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('edit/<int:entry_id>/', diary_edit, name='diary_edit'),
    path('delete/<int:entry_id>/', diary_delete, name='diary_delete'),
    path('api/diary/', DiaryEntryListCreateAPIView.as_view(), name='diary-list-create'),
    path('api/diary/<int:pk>/', DiaryEntryDetailAPI.as_view(), name='diary-detail'),
    # urls.py
    path('change-password/', PasswordChangeView.as_view(template_name='diary/change_password.html'), name='change_password'),
     path('api/register/', UserRegisterAPIView.as_view(), name='api-register'),
     path('api/diary/day/<str:date_str>/', EntriesByDayAPIView.as_view(), name='entries_by_day_api'),
     path('archive/<int:entry_id>/', archive_entry, name='archive_entry'),
    path('unarchive/<int:entry_id>/', unarchive_entry, name='unarchive_entry'),
    path('archived/', archived_entries, name='archived_entries'),
    path('profil/', profile_update, name='profile'),
    path('profil/',profile_update, name='profile_update'),
    
    # API Router
    path('api/', include(router.urls)),

    # JWT Token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Search and Calendar views
    path('search/', diary_search, name='diary_search'),
    path('calendar/', calendar_view, name='calendar_view'),

    # API calendar events (APIView kullanılarak)
    path('api/calendar-events/', CalendarEventsAPIView.as_view(), name='calendar_events'),

    path('calendar/day/<str:date>/', entries_by_day, name='entries_by_day'),

    # Token alma endpoint (login sonrası token almak için)
    path('get-token/', get_token, name='get_token'),

    #şifre değitirme sonrası mesaj sayfası
    path('sifre-degistir/', PasswordChangeView.as_view(
        template_name='diary/change_password.html',
        success_url='/sifre-degistir-tamamlandi/'
    ), name='change_password'),
    path('sifre-degistir-tamamlandi/', PasswordChangeDoneView.as_view(
        template_name='diary/change_password_done.html'
    ), name='password_change_done'),

    path('diary/<int:entry_id>/pdf/', diary_pdf, name='diary_pdf'),

     #fotoğraf galerisi 
    path('galeri/', photo_gallery, name='photo_gallery'),
    #fotoğraf silme butonu
    path('photo/<int:photo_id>/delete/', photo_delete, name='photo_delete'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('async-hello/', async_hello, name='async_hello'),
]
