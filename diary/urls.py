from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import DiaryEntryViewSet, CalendarEventsAPIView , DiaryEntryListCreateAPIView , DiaryEntryDetailAPI
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'diary', DiaryEntryViewSet, basename='diary')

urlpatterns = [
    path('', views.home, name='home'),
    path('diary/', views.diary_list, name='diary_list'),
    path('diary/new/', views.diary_create, name='diary_create'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit/<int:entry_id>/', views.diary_edit, name='diary_edit'),
    path('delete/<int:entry_id>/', views.diary_delete, name='diary_delete'),
    path('api/diary/', DiaryEntryListCreateAPIView.as_view(), name='diary-list-create'),
    path('api/diary/<int:pk>/', DiaryEntryDetailAPI.as_view(), name='diary-detail'),

    # API Router
    path('api/', include(router.urls)),

    # JWT Token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Search and Calendar views
    path('search/', views.diary_search, name='diary_search'),
    path('calendar/', views.calendar_view, name='calendar_view'),

    # API calendar events (APIView kullanılarak)
    path('api/calendar-events/', CalendarEventsAPIView.as_view(), name='calendar_events'),

    path('calendar/day/<str:date>/', views.entries_by_day, name='entries_by_day'),

    # Token alma endpoint (login sonrası token almak için)
    path('get-token/', views.get_token, name='get_token'),
]
