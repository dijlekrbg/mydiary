from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from ..serializers import DiaryEntrySerializer, UserRegisterSerializer,DiaryEntryCreateSerializer
from ..models import DiaryEntry
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required   
from datetime import datetime
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404, redirect , render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa




class DiaryEntryListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entries = DiaryEntry.objects.filter(user=request.user).order_by('-created_at')
        serializer = DiaryEntrySerializer(entries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DiaryEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CalendarEventsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entries = DiaryEntry.objects.filter(user=request.user)
        events = []
        for entry in entries:
            events.append({
                'title': entry.title,
                'start': entry.created_at.date().isoformat(),
                'color': '#3498db'
            })
        return Response(events)
    

@login_required
def calendar_events(request):
    entries = DiaryEntry.objects.filter(user=request.user)
    events = []
    for entry in entries:
        events.append({
            'title': entry.title,
            'start': entry.created_at.date().isoformat(),
            'color': '#3498db'
        })
    return JsonResponse(events, safe=False)


class DiaryEntryViewSet(viewsets.ModelViewSet):
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DiaryEntryCreateSerializer
        return DiaryEntrySerializer

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user).order_by('-created_at')
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DiaryEntryDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return DiaryEntry.objects.get(pk=pk, user=user)
        except DiaryEntry.DoesNotExist:
            raise NotFound(detail="Entry bulunamadı")

    def get(self, request, pk):
        entry = self.get_object(pk, request.user)
        serializer = DiaryEntrySerializer(entry)
        return Response(serializer.data)

    def put(self, request, pk):
        entry = self.get_object(pk, request.user)
        serializer = DiaryEntrySerializer(entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        entry = self.get_object(pk, request.user)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@login_required
def get_token(request):
    user = request.user
    refresh = RefreshToken.for_user(user)
    return JsonResponse({'access': str(refresh.access_token)})



class UserRegisterAPIView(APIView):
    permission_classes = []  # Herkes erişebilir

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Kayıt başarılı!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class EntriesByDayAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, date_str):
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Tarih formatı yanlış. Yıl-Ay-Gün (YYYY-MM-DD) olmalı.'}, status=400)

        entries = DiaryEntry.objects.filter(user=request.user, created_at__date=selected_date)
        serializer = DiaryEntrySerializer(entries, many=True)
        return Response(serializer.data)
    
    

@login_required
def archive_entry(request, entry_id):
    entry = get_object_or_404(DiaryEntry, id=entry_id, user=request.user)
    entry.is_archived = True
    entry.save()
    return redirect('dashboard')

@login_required
def unarchive_entry(request, entry_id):
    entry = get_object_or_404(DiaryEntry, id=entry_id, user=request.user)
    entry.is_archived = False
    entry.save()
    return redirect('archived_entries')
@login_required
def archived_entries(request):
    entries = DiaryEntry.objects.filter(user=request.user, is_archived=True).order_by('-created_at')
    return render(request, 'diary/archived_entries.html', {'entries': entries})





