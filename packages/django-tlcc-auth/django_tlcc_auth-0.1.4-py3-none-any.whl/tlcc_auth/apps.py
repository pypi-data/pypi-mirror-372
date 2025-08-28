from django.apps import AppConfig

class TlccAuthConfig(AppConfig): #Signals importeren + modules zo inladen op veilige plek (beter volgens internet)
    name = "tlcc_auth"
    verbose_name = "TLCC Auth"

    def ready(self):
        from . import signals
