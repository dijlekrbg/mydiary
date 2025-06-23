from django.db import models
from django.contrib.auth.models import User

class DiaryEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    photo = models.ImageField(upload_to='diary_photos/', blank=True, null=True) 
    is_favorite = models.BooleanField(default=False)  
    tags = models.CharField(max_length=200, blank=True) 
    is_archived = models.BooleanField(default=False)  
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"

class Photo(models.Model):
    diary_entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Photo for {self.diary_entry.title}"
