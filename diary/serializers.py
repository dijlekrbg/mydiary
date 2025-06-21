from rest_framework import serializers
from .models import DiaryEntry


class CalendarEventSerializer(serializers.Serializer):
    date = serializers.DateField()


class DiaryEntrySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = DiaryEntry
        fields = ['id', 'user', 'title', 'content', 'created_at', 'updated_at', 'photo']

