from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from ..forms import DiaryEntryForm,PhotoForm
from ..models import DiaryEntry , Photo
from django.contrib import messages
from django.db.models import Q
import datetime,calendar
from ..forms import ProfileUpdateForm
from django.contrib import messages
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa



def home(request):
    return render(request, 'diary/home.html')

@login_required
def diary_list(request):
    entries = DiaryEntry.objects.filter(user=request.user,is_archived =False).order_by('-created_at')
    return render(request, 'diary/diary_list.html', {'entries': entries})

@login_required
def diary_create(request):
    if request.method == 'POST':
        form = DiaryEntryForm(request.POST, request.FILES)
        photo_form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            diary_entry = form.save(commit=False)
            diary_entry.user = request.user
            diary_entry.save()
            for img in request.FILES.getlist('images'):
                Photo.objects.create(diary_entry=diary_entry, image=img)
            messages.success(request, 'Günlük başarıyla oluşturuldu.')
            return redirect('diary_list')
            
        else:
            messages.error(request, "Formda hata var:" + str(form.errors))
    else:
        form = DiaryEntryForm()
        photo_form = PhotoForm()
    return render(request, 'diary/diary_form.html', {'form': form, 'photo_form': photo_form})



@login_required
def calendar_view(request):
    today = datetime.date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    cal = calendar.HTMLCalendar(firstweekday=0)
    html_cal = cal.formatmonth(year, month)

    entries = DiaryEntry.objects.filter(
        user=request.user,
        created_at__year=year,
        created_at__month=month
    )
    entry_days = set(entry.created_at.day for entry in entries)

    return render(request, 'diary/calendar.html', {
        'calendar': html_cal,
        'year': year,
        'month': month,
        'entry_days': list(entry_days),
    })

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
def diary_search(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = DiaryEntry.objects.filter(
            Q(user=request.user) &
            (Q(title__icontains=query) | Q(content__icontains=query))
        ).order_by('-created_at')
    return render(request, 'diary/diary_search.html', {'results': results, 'query': query})

@login_required
def diary_delete(request, entry_id):
    entry = DiaryEntry.objects.get(id=entry_id, user=request.user)
    if request.method == 'POST':
        entry.delete()
        return redirect('dashboard')
    return render(request, 'diary/diary_confirm_delete.html', {'entry': entry})




@login_required
def entries_by_day(request, date):
    selected_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    entries = DiaryEntry.objects.filter(user=request.user, created_at__date=selected_date)
    return render(request, 'diary/entries_by_day.html', {'entries': entries, 'date': selected_date})


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
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    query = request.GET.get('q')
    entries = DiaryEntry.objects.filter(user=request.user, is_archived=False).order_by('-created_at')
    archived_entries =DiaryEntry.objects.filter(user=request.user, is_archived=True).order_by('-created_at') 
    if query:
        entries = entries.filter(title__icontains=query) | entries.filter(content__icontains=query)
    entries = entries.order_by('-created_at')
    return render(request, 'diary/dashboard.html', {
    'entries': entries,
    'archived_entries' : archived_entries
    })


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




@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profiliniz güncellendi.')
            return redirect('profile_update')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'diary/profile_update.html', {'form': form})


@login_required
def diary_pdf(request, entry_id):
    entry = get_object_or_404(DiaryEntry, id=entry_id, user=request.user)
    template_path = 'diary/diary_pdf.html'
    context = {'entry': entry}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{entry.title}.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF oluşturulamadı')
    return response


@login_required
def photo_gallery(request):
    photos = Photo.objects.filter(diary_entry__user=request.user)
    return render(request, 'diary/photo_gallery.html', {'photos': photos})








