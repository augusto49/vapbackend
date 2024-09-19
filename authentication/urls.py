from django.urls import path
from .views import (
        AcceptRideRequestView,
        CalculateRouteView,
        CancelRideByDriverView,
        CancelRideByPassengerView,
        CreateRideRequestView,
        DriverLoginView,
        DriverLogoutApiView,
        DriverProfileView,
        DriverStatusView,
        PassengerLogoutApiView,
        PassengerProfileView,
        PassengerRegisterView,
        DriverRegisterView,
        ToggleOnlineStatusView,
        UpdateDriverLocationView,
        VerifyUserEmail,
        PassengerLoginView,
        PasswordResetConfirm,
        PasswordResetRequestView,
        SetNewPasswordView)
from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
    
    # URL para refresh de token JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # URL comum para verificação de email
    path('verify-email/', VerifyUserEmail.as_view(), name='verify-email'),
    # URLs para reset de senha
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    
    ###### Passageiro ######
    # URLs para Passageiros
    path('passenger/register/', PassengerRegisterView.as_view(), name='register-passenger'),
    # URLs para login
    path('passenger/login/', PassengerLoginView.as_view(), name='login-passenger'),
    # URLs para perfil
    path('passenger/profile/', PassengerProfileView.as_view(), name='passenger-profile'),
    # URL para Passageiro.
    path('passenger/logout/', PassengerLogoutApiView.as_view(), name='passenger_logout'),
    # URL para calcular e rota.
    path('passenger/calculate-route/', CalculateRouteView.as_view(), name='calculate_route'),
    # URLs para solicitação de corrida.
    path('passenger/ride-request/', CreateRideRequestView.as_view(), name='create-ride-request'),
    # URLs para cancelar corridas
    path('ride/cancel/passenger/<int:user_id>/', CancelRideByPassengerView.as_view(), name='cancel-ride-passenger'),
    
    ###### Motorista ######
    # URLs para login
    path('driver/login/', DriverLoginView.as_view(), name='login-driver'),
    # URLs para Motoristas
    path('driver/register/', DriverRegisterView.as_view(), name='register-driver'),
    # URLs para perfil
    path('profile/driver/', DriverProfileView.as_view(), name='driver-profile'),
    # URL para Motorista
    path('driver/logout/', DriverLogoutApiView.as_view(), name='driver_logout'), 
    # URL atualizar localização do motorista.
    path('driver/location/<int:user_id>/', UpdateDriverLocationView.as_view(), name='update-driver-location'),
    # URL para alternar status online/offline
    path('driver/toggle-online-status/<int:user_id>/', ToggleOnlineStatusView.as_view(), name='toggle-online-status'),
    path('driver/driver-status/<int:user_id>/', DriverStatusView.as_view(), name='driver-status'),
    # URL para aceitar corrida
    path('ride/accept/<int:ride_id>/', AcceptRideRequestView.as_view(), name='accept-ride'),
    # URLs para cancelar corridas
    path('ride/cancel/driver/<int:user_id>/', CancelRideByDriverView.as_view(), name='cancel-ride-driver'),
]