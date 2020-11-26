from django.contrib import admin
from .models import (
    Settings,
    SocialMedia,
    ContactForm,
    Opinion,
    OneSignal
)

admin.site.register(Settings)
admin.site.register(SocialMedia)
admin.site.register(ContactForm)
admin.site.register(Opinion)
admin.site.register(OneSignal)
