from django.contrib import admin


# ================================ Modal ======================================
from .models import ModalImageOnly, ModalSingleBG, ModalLinkVideo, ModalRotateBG


class ImageOnlyAdmin(admin.ModelAdmin):
    list_display = ('modal_title', 'activate')


class SingleBGAdmin(admin.ModelAdmin):
    list_display = ('h1', 'activate')


class LinkVideoAdmin(admin.ModelAdmin):
    list_display = ('h2', 'activate')


class RotateBGAdmin(admin.ModelAdmin):
    list_display = ('h2', 'activate')


admin.site.register(ModalImageOnly, ImageOnlyAdmin)
admin.site.register(ModalSingleBG, SingleBGAdmin)
admin.site.register(ModalLinkVideo, LinkVideoAdmin)
admin.site.register(ModalRotateBG, RotateBGAdmin)


# ===================================== Calendar ================================
from .models import Calendar, Event, EventType


class CalendarAdmin(admin.ModelAdmin):
    list_display = ('modal_title', 'activate')

class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_of_event', 'calendar', 'event_type')


admin.site.register(Calendar, CalendarAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Event, EventAdmin)


# ============================ Portfolio =========================================
from .models import Portfolio, PortfolioCategory


class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'filter')
    search_fields = ['title']


admin.site.register(PortfolioCategory)
admin.site.register(Portfolio, PortfolioAdmin)


# ================================ Blog =========================================
from .models import BlogPost, BlogCategory, Profile
from markdownx.admin import MarkdownxModelAdmin


admin.site.register(BlogPost, MarkdownxModelAdmin)
admin.site.register(BlogCategory)
admin.site.register(Profile)
