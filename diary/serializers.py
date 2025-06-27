from rest_framework import serializers
from .models import DiaryEntry,Photo
from django.contrib.auth.models import User



class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class CalendarEventSerializer(serializers.Serializer):
    date = serializers.DateField()


class DiaryEntrySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = DiaryEntry
        fields = ['id', 'user', 'title', 'content', 'created_at', 'updated_at', 'photo','is_favorite', 'tags']




class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'image', 'uploaded_at']

class DiaryEntrySerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True, source='photos')

    class Meta:
        model = DiaryEntry
        fields = ['id', 'title', 'content', 'created_at', 'is_favorite', 'is_archived', 'tags', 'photos']

class DiaryEntryCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(max_length=100000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = DiaryEntry
        fields = ['title', 'content', 'is_favorite', 'is_archived', 'tags', 'images']

    def create(self, validated_data):
        try:
            images = validated_data.pop('images', [])
            user=self.context['request'].user
            
            diary_entry = DiaryEntry.objects.create(**validated_data)
            for image in images:
                Photo.objects.create(diary_entry=diary_entry, image=image)
            return diary_entry
        except Exception as e:
            print("create() hatası :",e)
            raise e

