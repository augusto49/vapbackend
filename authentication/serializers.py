from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.gis.geos import Point

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import User, PassengerProfile, DriverProfile, RideRequest, DriverLocation
from .utils import send_normal_email

# Serializer para o registro de motoristas
class DriverRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2= serializers.CharField(max_length=68, min_length=6, write_only=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    cidade = serializers.CharField(source='driverprofile.cidade')
    telefone = serializers.CharField(source='driverprofile.telefone')
    cpf = serializers.CharField(source='driverprofile.cpf')
    data_nascimento = serializers.DateField(source='driverprofile.data_nascimento')
    genero = serializers.CharField(source='driverprofile.genero')
    chave_pix = serializers.CharField(source='driverprofile.chave_pix', required=False)
    foto_rosto = serializers.ImageField(source='driverprofile.foto_rosto', required=False)
    cep = serializers.CharField(source='driverprofile.cep')
    endereco = serializers.CharField(source='driverprofile.endereco')
    numero = serializers.CharField(source='driverprofile.numero')
    complemento = serializers.CharField(source='driverprofile.complemento', required=False)
    bairro = serializers.CharField(source='driverprofile.bairro')
    uf = serializers.CharField(source='driverprofile.uf')
    cnh_documento = serializers.FileField(source='driverprofile.cnh_documento', required=False)
    veiculo_documento = serializers.FileField(source='driverprofile.veiculo_documento', required=False)
    placa_veiculo = serializers.CharField(source='driverprofile.placa_veiculo')
    modelo_veiculo = serializers.CharField(source='driverprofile.modelo_veiculo')
    ano_veiculo = serializers.IntegerField(source='driverprofile.ano_veiculo')
    cor_veiculo = serializers.CharField(source='driverprofile.cor_veiculo')
    termo_aceite = serializers.BooleanField(source='driverprofile.termo_aceite')

    class Meta:
        model=User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'password', 'password2', 'cidade',
            'telefone', 'cpf', 'data_nascimento', 'genero', 'chave_pix', 'foto_rosto',
            'cep', 'endereco', 'numero', 'complemento', 'bairro', 'uf', 'cnh_documento',
            'veiculo_documento', 'placa_veiculo', 'modelo_veiculo', 'ano_veiculo',
            'cor_veiculo', 'termo_aceite'
        ]

    def validate(self, attrs):
        password=attrs.get('password', '')
        password2 =attrs.get('password2', '')
        if password !=password2:
            raise serializers.ValidationError("passwords do not match")
         
        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('driverprofile')
        user= User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data.get('password'),
            is_driver=True
            )
        DriverProfile.objects.create(user=user, **profile_data)
        return user

# Serializer para o registro de passageiros
class PassengerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2= serializers.CharField(max_length=68, min_length=6, write_only=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    cidade = serializers.CharField(source='passengerprofile.cidade')
    foto = serializers.ImageField(source='passengerprofile.foto', required=False)
    telefone = serializers.CharField(source='passengerprofile.telefone')
    cpf = serializers.CharField(source='passengerprofile.cpf')
    data_nascimento = serializers.DateField(source='passengerprofile.data_nascimento')
    genero = serializers.CharField(source='passengerprofile.genero')
    termo_aceite = serializers.BooleanField(source='passengerprofile.termo_aceite')

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'password', 'password2',
            'cidade', 'foto', 'telefone', 'cpf', 'data_nascimento',
            'genero', 'termo_aceite']
    
    def validate(self, attrs):
        password=attrs.get('password', '')
        password2 =attrs.get('password2', '')
        if password !=password2:
            raise serializers.ValidationError("passwords do not match")
         
        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('passengerprofile')
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data.get('password'),
            is_passenger=True
        )
        PassengerProfile.objects.create(user=user, **profile_data)
        return user

# Serializer para o perfil passageiro.
class PassengerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassengerProfile
        fields = '__all__'

# Serializer para o perfil motorista.
class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = '__all__'

# Serializer para o login
class LoginSerializer(serializers.Serializer):
    is_passenger = serializers.BooleanField(read_only=True)
    is_driver = serializers.BooleanField(read_only=True)
    email = serializers.EmailField(max_length=155, min_length=6)
    password=serializers.CharField(max_length=68, write_only=True)
    full_name=serializers.CharField(max_length=255, read_only=True)
    access_token=serializers.CharField(max_length=255, read_only=True)
    refresh_token=serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token', 'is_driver', 'is_passenger']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request=self.context.get('request')
        
        # Autentica o usuário
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("invalid credential try again")
        
        # Verifica se o email do usuário foi verificado
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified")
        
        # Verifica o status do motorista
        if user.is_driver:
            if not hasattr(user, 'driverprofile') or user.driverprofile.status != 'approved':
                raise AuthenticationFailed('Driver account not approved. Awaiting evaluation.')
        elif user.is_passenger:
            if not hasattr(user, 'passengerprofile'):
                raise AuthenticationFailed('Passenger profile does not exist.')
            
        # Gera tokens de acesso e refresh
        tokens=user.tokens()
        return {
            "is_passenger": user.is_passenger,
            "is_driver": user.is_driver,
            'email':user.email,
            'full_name':user.get_full_name,
            "access_token":str(tokens.get('access')),
            "refresh_token":str(tokens.get('refresh'))
        }

# Serializer para requisição de redefinição de senha
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    user_type = serializers.ChoiceField(choices=[('passenger', 'Passenger'), ('driver', 'Driver')])

    class Meta:
        fields = ['email', 'user_type']

    def validate(self, attrs):
        
        email = attrs.get('email')
        user_type = attrs.get('user_type')
        
        # Verifica se o email está associado a um usuário do tipo correto
        if user_type == 'driver':
            if not User.objects.filter(email=email, is_driver=True).exists():
                raise serializers.ValidationError("Driver with this email does not exist.")
            user = User.objects.get(email=email, is_driver=True)
        elif user_type == 'passenger':
            if not User.objects.filter(email=email, is_passenger=True).exists():
                raise serializers.ValidationError("Passenger with this email does not exist.")
            user = User.objects.get(email=email, is_passenger=True)
        else:
            raise serializers.ValidationError("Invalid user type.")
        
        if User.objects.filter(email=email).exists():
            user= User.objects.get(email=email)
            uidb64=urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            frontend_domain = settings.FRONTEND_URL
            frontend_path = f"/password-reset-confirm/{uidb64}/{token}/"
            abslink=f"{frontend_domain}{frontend_path}"
            print(abslink)
            email_body=f"Hi {user.first_name} use the link below to reset your password {abslink}"
            data={
                'email_body':email_body, 
                'email_subject':"Reset your Password", 
                'to_email':user.email
                }
            send_normal_email(data)

        return super().validate(attrs)

# Serializer para definir uma nova senha
class SetNewPasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64=serializers.CharField(min_length=1, write_only=True)
    token=serializers.CharField(min_length=3, write_only=True)

    class Meta:
        fields = ['password', 'confirm_password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')
            uidb64 = attrs.get('uidb64')
            token = attrs.get('token')
            
            if password != confirm_password:
                raise serializers.ValidationError({"password": "Passwords do not match."})

            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)
            
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("reset link is invalid or has expired", 401)
            
            user.set_password(password)
            user.save()
            
            return user
        except Exception as e:
            return AuthenticationFailed("link is invalid or has expired")

# Serializer para logout
class LogoutUserSerializer(serializers.Serializer):
    refresh_token=serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')

        return attrs

    def save(self, **kwargs):
        try:
            token=RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail('bad_token')

# Solicitação de corrida
class RideRequestSerializer(serializers.ModelSerializer):
    start_location = serializers.SerializerMethodField()
    end_location = serializers.SerializerMethodField()
    distance = serializers.FloatField(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = RideRequest
        fields = ['start_location', 'end_location', 'distance', 'price']

    def get_start_location(self, obj):
        if obj.start_location:
            return {
                'type': 'Point',
                'coordinates': [obj.start_location.x, obj.start_location.y]
            }
        return None

    def get_end_location(self, obj):
        if obj.end_location:
            return {
                'type': 'Point',
                'coordinates': [obj.end_location.x, obj.end_location.y]
            }
        return None

    def create(self, validated_data):
        start_location_data = self.initial_data.get('start_location', {})
        end_location_data = self.initial_data.get('end_location', {})

        start_location = Point(start_location_data['coordinates'][0], start_location_data['coordinates'][1], srid=4326)
        end_location = Point(end_location_data['coordinates'][0], end_location_data['coordinates'][1], srid=4326)

        ride_request = RideRequest.objects.create(
            start_location=start_location,
            end_location=end_location,
            **validated_data
        )
        return ride_request
    
# Aceitar corrida
class AcceptRideRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideRequest
        fields = ['id', 'driver', 'status']
        read_only_fields = ['id']

    def validate(self, attrs):
        ride_request = self.instance
        if ride_request.status != 'pending':
            raise serializers.ValidationError("Only pending rides can be accepted.")
        return attrs

    def accept(self, driver):
        self.instance.driver = driver
        self.instance.status = 'accepted'
        self.instance.save()

# Localização do motorista para solicitação
class DriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocation
        fields = ['driver', 'location', 'updated_at']
        read_only_fields = ['driver', 'updated_at']

# Botão online e off do motorista
class ToggleOnlineStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = ['is_online']

# Cancelamento de corrida
class CancelRideRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideRequest
        fields = ['id', 'status', 'canceled_by']
        read_only_fields = ['id']

    def validate(self, attrs):
        ride_request = self.instance
        if ride_request.status not in ['pending', 'accepted']:
            raise serializers.ValidationError("Cannot cancel a ride that is not pending or accepted.")
        return attrs

    def cancel_by_passenger(self):
        self.instance.status = 'canceled'
        self.instance.canceled_by = 'passenger'
        self.instance.save()

    def cancel_by_driver(self):
        self.instance.status = 'canceled'
        self.instance.canceled_by = 'driver'
        self.instance.save()