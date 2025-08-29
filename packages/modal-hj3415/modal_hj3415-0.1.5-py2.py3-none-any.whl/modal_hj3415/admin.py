from django.contrib import admin

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
