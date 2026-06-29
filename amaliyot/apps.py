from django.apps import AppConfig



class AmaliyotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'amaliyot'

    def ready(self):
        import amaliyot.tasks  






























