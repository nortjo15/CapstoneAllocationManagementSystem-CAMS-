from django.contrib import admin
from admin_app.models import CapstoneInformationSection, CapstoneInformationContent, UnitContacts

@admin.register(CapstoneInformationSection)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id","name","order","parent_section")
    list_editable = ("order",)
    search_fields = ("name",)

@admin.register(CapstoneInformationContent)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("id","title","section_id","status","pinned","priority","published_at","expires_at","author")
    list_filter  = ("status","pinned","section_id")
    search_fields = ("title","body","author")
    autocomplete_fields = ("section_id",)

@admin.register(UnitContacts)
class UnitContactsAdmin(admin.ModelAdmin):
    list_display = ("name","email","phone","updated_at")
    search_fields = ("name","email")