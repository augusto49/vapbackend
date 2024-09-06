from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.managers import UserManager

AUTH_PROVIDERS ={'email':'email', 'google':'google', 'github':'github', 'linkedin':'linkedin'}

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True, editable=False) 
    email = models.EmailField(
        max_length=255, verbose_name=_("Email Address"), unique=True
    )
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_passenger = models.BooleanField(default=False)
    is_driver = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    auth_provider=models.CharField(max_length=50, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()
    
    def tokens(self):    
        refresh = RefreshToken.for_user(self)
        return {
            "refresh":str(refresh),
            "access":str(refresh.access_token)
        }

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"

# Modelo de perfil para passageiros, relacionado ao modelo de usuário.
class PassengerProfile(models.Model):
    is_active = models.BooleanField(default=True)
    # Relacionamento one-to-one com o usuário.
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Campos adicionais para o perfil do passageiro.
    cidade = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='uploads/passenger_photos/', null=True, blank=True)
    telefone = models.CharField(max_length=20)
    cpf = models.CharField(max_length=11, unique=True)
    data_nascimento = models.DateField()
    genero = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')])
    termo_aceite = models.BooleanField(default=False)

# Modelo de perfil para motoristas, relacionado ao modelo de usuário.
class DriverProfile(models.Model):
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    # Relacionamento one-to-one com o usuário.
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # Campos adicionais para o perfil do motorista.
    cidade = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    cpf = models.CharField(max_length=11, unique=True)
    data_nascimento = models.DateField()
    genero = models.CharField(max_length=10, choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')])
    chave_pix = models.CharField(max_length=100, null=True, blank=True)
    foto_rosto = models.ImageField(upload_to='uploads/driver_photos/', null=True, blank=True)
    cep = models.CharField(max_length=10)
    endereco = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.CharField(max_length=50)
    uf = models.CharField(max_length=2)
    cnh_documento = models.FileField(upload_to='uploads/driver_documents/', null=True, blank=True)
    veiculo_documento = models.FileField(upload_to='uploads/vehicle_documents/', null=True, blank=True)
    placa_veiculo = models.CharField(max_length=10)
    modelo_veiculo = models.CharField(max_length=50)
    ano_veiculo = models.IntegerField()
    cor_veiculo = models.CharField(max_length=20)
    termo_aceite = models.BooleanField(default=False)
    
class OneTimePassword(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    otp=models.CharField(max_length=6)

    def __str__(self):
        return f"{self.user.first_name} - otp code"

# Modelo para solicitação de corrida
class RideRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('accepted', 'Aceito'),
        ('on_route', 'Em Rota'),
        ('completed', 'Concluído'),
        ('canceled', 'Cancelado'),
    ]

    CANCELED_BY_CHOICES = [
        ('passenger', 'Passageiro'),
        ('driver', 'Motorista'),
        ('none', 'Nenhum'),
    ]

    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ride_requests')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_rides', null=True, blank=True)
    start_location = gis_models.PointField(_("Local de Partida"), geography=True)
    end_location = gis_models.PointField(_("Local de Destino"), geography=True)
    distance = models.FloatField(null=True, blank=True)  # Novo campo para distância
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Novo campo para preço
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    canceled_by = models.CharField(max_length=10, choices=CANCELED_BY_CHOICES, default='none')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Solicitação de corrida de {self.passenger.get_full_name}"

# Modelo para localização do motorista
class DriverLocation(models.Model):
    driver = models.OneToOneField(User, on_delete=models.CASCADE, related_name='current_location')
    location = gis_models.PointField(_("Localização Atual"), geography=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Driver: {self.driver.get_full_name} Location: {self.location}"