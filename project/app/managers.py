from django.contrib.auth.models import UserManager
from safedelete.managers import SafeDeleteManager

class UsuarioManager(SafeDeleteManager, UserManager):
    pass
