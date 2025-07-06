# operations/apps.py

from django.apps import AppConfig

class OperationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'operations'

    # ▼▼▼ هذا هو الجزء الجديد الذي يقوم بتفعيل الإشارات ▼▼▼
    def ready(self):
        import operations.signals