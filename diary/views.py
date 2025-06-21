from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import DiaryEntry
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import DiaryEntryForm
from django.contrib import messages
from rest_framework import viewsets, permissions, filters , status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import DiaryEntrySerializer
from django.db.models import Q
import datetime

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

@login_required
def calendar_view(request):
    return render(request, 'diary/calendar.html')

def home(request):
    return render(request, 'diary/home.html')

@login_required
def entries_by_day(request, date):
    selected_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    entries = DiaryEntry.objects.filter(user=request.user, created_at__date=selected_date)
    return render(request, 'diary/entries_by_day.html', {'entries': entries, 'date': selected_date})

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

@login_required
def diary_list(request):
    entries = DiaryEntry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'diary/diary_list.html', {'entries': entries})

@login_required
def diary_create(request):
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST, request.FILES)
        if form.is_valid():
            diary_entry = form.save(commit=False)
            diary_entry.user = request.user
            diary_entry.save()
            return redirect('diary_list')
    else:
        form = DiaryEntryForm()
    return render(request, 'diary/diary_form.html', {'form': form})

@login_required
def diary_edit(request, entry_id):
    entry = DiaryEntry.objects.get(id=entry_id, user=request.user)
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = DiaryEntryForm(instance=entry)
    return render(request, 'diary/diary_form.html', {'form': form, 'edit': True})

@login_required
def diary_delete(request, entry_id):
    entry = DiaryEntry.objects.get(id=entry_id, user=request.user)
    if request.method == 'POST':
        entry.delete()
        return redirect('dashboard')
    return render(request, 'diary/diary_confirm_delete.html', {'entry': entry})

@login_required
def diary_search(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = DiaryEntry.objects.filter(
            Q(user=request.user) &
            (Q(title__icontains=query) | Q(content__icontains=query))
        ).order_by('-created_at')
    return render(request, 'diary/diary_search.html', {'results': results, 'query': query})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Kayıt formunda hata var.")
    else:
        form = UserCreationForm()
    return render(request, 'diary/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            serializer = TokenObtainPairSerializer(data={
                "username": request.POST.get("username"),
                "password": request.POST.get("password")
            })

            if serializer.is_valid():
                access_token = serializer.validated_data['access']
                refresh_token = serializer.validated_data['refresh']
                return render(request, 'diary/login_success.html', {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                })
            else:
                messages.error(request, "Token alınamadı")
        else:
            messages.error(request, "Giriş bilgileri hatalı")
    else:
        form = AuthenticationForm()
    return render(request, 'diary/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def dashboard(request):
    query = request.GET.get('q')
    entries = DiaryEntry.objects.filter(user=request.user).order_by('-created_at')
    if query:
        entries = entries.filter(title__icontains=query) | entries.filter(content__icontains=query)
    entries = entries.order_by('-created_at')
    return render(request, 'diary/dashboard.html', {'entries': entries})

class DiaryEntryViewSet(viewsets.ModelViewSet):
    serializer_class = DiaryEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user)

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
