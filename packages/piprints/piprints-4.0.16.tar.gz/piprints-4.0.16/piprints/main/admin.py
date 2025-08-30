from .models import *
from django.contrib import admin

class BaseAdmin(admin.ModelAdmin):
    pass

class UserAdmin(BaseAdmin):
    list_display = ('username','is_active','is_staff','is_superuser')
    list_filter = ('is_active','is_staff','is_superuser')
    search_fields = ('username',)

admin.site.register(User,UserAdmin)

admin.site.register(Person)

admin.site.register(Paper)

admin.site.register(News)

class EventAdmin(BaseAdmin):
    list_display = ('date_from','title')
    list_display_links = ('title',)

admin.site.register(Event,EventAdmin)

class SeminarAdmin(BaseAdmin):
    list_display = ('date','all_speakers','title')
    list_display_links = ('title',)

    def all_speakers(self,obj):
        return ' - '.join([x.lastname for x in obj.speakers.all()])

admin.site.register(Seminar,SeminarAdmin)

admin.site.register(Document)

class TemplateAdmin(BaseAdmin):
    list_display = ('name','event')
    list_display_links = ('event',)
    save_as = True

admin.site.register(Template,TemplateAdmin)

class EventParticipantAdmin(BaseAdmin):
    list_display = ('creation_time','event','lastname','firstname','state','grant_state')
    list_display_links = ('lastname','firstname')

admin.site.register(EventParticipant,EventParticipantAdmin)

def ignore_person_requests(modeladmin, request, qs):
    qs.update(managed = True)

class PersonRequestAdmin(BaseAdmin):    
    list_display = ('managed','lastname','firstname','creation_time')
    list_display_links = ('lastname','firstname')
    actions = [ignore_person_requests]

admin.site.register(PersonRequest,PersonRequestAdmin)

class TagAdmin(BaseAdmin):
    pass

admin.site.register(Tag,TagAdmin)

class ResearchProjectAdmin(BaseAdmin):
    pass

admin.site.register(ResearchProject, ResearchProjectAdmin)

class SiteParametersAdmin(admin.ModelAdmin):
    pass

admin.site.register(SiteParameters, SiteParametersAdmin)