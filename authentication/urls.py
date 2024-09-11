from django.urls import path
from .views import (
        AcceptRideRequestView,
        CancelRideByDriverView,
        CancelRideByPassengerView,
        CreateRideRequestView,
        DriverLoginView,
        DriverProfileView,
        DriverStatusView,
        PassengerProfileView,
        PassengerRegisterView,
        DriverRegisterView,
        ToggleOnlineStatusView,
        UpdateDriverLocationView,
        VerifyUserEmail,
        PassengerLoginView,
        PasswordResetConfirm,
        PasswordResetRequestView,
        SetNewPasswordView,
        LogoutApiView)
from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
    # URLs para Passageiros
    path('passenger/register/', PassengerRegisterView.as_view(), name='register-passenger'),
    
    # URLs para Motoristas
    path('driver/register/', DriverRegisterView.as_view(), name='register-driver'),
    
    # URLs para login
    path('login/driver/', DriverLoginView.as_view(), name='login-driver'),
    path('login/passenger/', PassengerLoginView.as_view(), name='login-passenger'),
    
    # URL comum para verificação de email
    path('verify-email/', VerifyUserEmail.as_view(), name='verify-email'),
    
    # URL para refresh de token JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # URLs para reset de senha
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='password-reset-confirm'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    
    # URLs para perfil
    path('profile/passenger/', PassengerProfileView.as_view(), name='passenger-profile'),
    path('profile/driver/', DriverProfileView.as_view(), name='driver-profile'),
    
    # URL para logout
    path('logout/', LogoutApiView.as_view(), name='logout'),
    
    # URLs para solicitação de corrida e localização do motorista
    path('ride-request/', CreateRideRequestView.as_view(), name='create-ride-request'),
    path('driver-location/', UpdateDriverLocationView.as_view(), name='update-driver-location'),
    
    # URL para alternar status online/offline
    path('driver/toggle-online-status/<int:user_id>/', ToggleOnlineStatusView.as_view(), name='toggle-online-status'),
    path('driver/driver-status/<int:user_id>/', DriverStatusView.as_view(), name='driver-status'),
    
    # URL para aceitar corrida
    path('ride/accept/<int:pk>/', AcceptRideRequestView.as_view(), name='accept-ride'),
    
    # URLs para cancelar corridas
    path('ride/cancel/passenger/<int:pk>/', CancelRideByPassengerView.as_view(), name='cancel-ride-passenger'),
    path('ride/cancel/driver/<int:pk>/', CancelRideByDriverView.as_view(), name='cancel-ride-driver'),
]