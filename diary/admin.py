from django.contrib import admin
from .models import DiaryEntry , Photo




class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height:100px;"/>'
        return ""
    image_preview.allow_tags = True
    image_preview.short_description = "Önizleme"

class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'is_favorite', 'is_archived')
    search_fields = ('title', 'content')
    list_filter = ('is_favorite', 'is_archived', 'created_at')
    inlines = [PhotoInline]

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('diary_entry', 'image', 'uploaded_at')
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height:100px;"/>'
        return ""
    image_preview.allow_tags = True
    image_preview.short_description = "Önizleme"

admin.site.register(DiaryEntry, DiaryEntryAdmin)
admin.site.register(Photo, PhotoAdmin)

admin.site.site_header = "Günlük Uygulaması Yönetimi"
admin.site.site_title ="Günlük Admin"
admin.site.index_title = "Günlük Yönetimi Paneli"