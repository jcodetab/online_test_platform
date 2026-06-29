from django.contrib import admin
from .models import Message
from .models import MessageTest,TestResult



class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'text', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)


admin.site.register(Message)


admin.site.register(MessageTest)
admin.site.register(TestResult)

