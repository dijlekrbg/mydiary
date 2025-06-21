# diary/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DiaryEntry
import os

@receiver(post_save, sender=DiaryEntry)
def backup_diary_entry(sender, instance, created, **kwargs):
    if created:
        backup_folder = 'backups'
        os.makedirs(backup_folder, exist_ok=True)

        filename = f"{backup_folder}/entry_{instance.id}.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"Başlık: {instance.title}\n")
            file.write(f"Tarih: {instance.created_at.strftime('%d-%m-%Y %H:%M')}\n")
            file.write(f"Kullanıcı: {instance.user.username}\n\n")
            file.write(f"İçerik:\n{instance.content}\n")
