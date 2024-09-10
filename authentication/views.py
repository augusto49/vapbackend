from .models import DriverLocation, RideRequest, User, PassengerProfile, DriverProfile
from django.shortcuts import render
from .utils import assign_nearest_driver, calculate_price, haversine_distance, send_generated_otp_to_email
from .models import OneTimePassword
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from .serializers import (
    AcceptRideRequestSerializer,
    CancelRideRequestSerializer,
    DriverLocationSerializer,
    DriverProfileSerializer,
    PassengerProfileSerializer,
    PassengerRegisterSerializer,
    DriverRegisterSerializer,
    LoginSerializer, 
    PasswordResetRequestSerializer,
    RideRequestSerializer, 
    SetNewPasswordSerializer, 
    LogoutUserSerializer,
    ToggleOnlineStatusSerializer
)
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

# View para registro de passageiros.
class PassengerRegisterView(GenericAPIView):
    serializer_class = PassengerRegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data = serializer.data
            send_generated_otp_to_email(user_data['email'], request)
            print(user_data)
            return Response({
                'data': user_data,
                'message':'thanks for signing up a passcode has be sent to verify your email'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# View para registro de motorista.
class DriverRegisterView(GenericAPIView):
    serializer_class = DriverRegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data = serializer.data
            send_generated_otp_to_email(user_data['email'], request)
            print(user_data)
            return Response({
                'data': user_data,
                'message':'thanks for signing up a passcode has be sent to verify your email'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View para verificar email otp.
class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        try:
            passcode = request.data.get('otp')
            user_pass_obj=OneTimePassword.objects.get(otp=passcode)
            user=user_pass_obj.user
            if not user.is_verified:
                user.is_verified=True
                user.save()
                return Response({
                    'message':'account email verified successfully'
                }, status=status.HTTP_200_OK)
            return Response({'message':'passcode is invalid user is already verified'}, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist as identifier:
            return Response({'message':'passcode not provided'}, status=status.HTTP_400_BAD_REQUEST) 

# View para login passageiro.        
class PassengerLoginView(GenericAPIView):
    serializer_class=LoginSerializer
    
    def post(self, request):
        serializer= self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Verifica se o usuário é passageiro
        if not data.get('is_passenger'):
            return Response({'detail': 'This login is only for passengers.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(data, status=status.HTTP_200_OK)

# View para login motorista.
class DriverLoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Verifica se o usuário é motorista
        if not data.get('is_driver'):
            return Response({'detail': 'This login is only for drivers.'}, status=status.HTTP_403_FORBIDDEN)
        
        return Response(data, status=status.HTTP_200_OK)

# View para reset de senha
class PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer

    def post(self, request):
        serializer=self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':'we have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        # return Response({'message':'user with that email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

# View para confirmar o reset de senha.
class PasswordResetConfirm(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id=smart_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'message':'credentials is valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)

# View para registrar a nova senha.
class SetNewPasswordView(GenericAPIView):
    serializer_class=SetNewPasswordSerializer

    def patch(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True, 'message':"password reset is succesful"}, status=status.HTTP_200_OK)

# Perfil passageiro.
class PassengerProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = PassengerProfile.objects.get(user=request.user)
            serializer = PassengerProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PassengerProfile.DoesNotExist:
            return Response({"detail": "Perfil não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            profile = PassengerProfile.objects.get(user=request.user)
            serializer = PassengerProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PassengerProfile.DoesNotExist:
            return Response({"detail": "Perfil não encontrado."}, status=status.HTTP_404_NOT_FOUND)

# Perfil motorista.
class DriverProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = DriverProfile.objects.get(user=request.user)
            serializer = DriverProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DriverProfile.DoesNotExist:
            return Response({"detail": "Perfil não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            profile = DriverProfile.objects.get(user=request.user)
            serializer = DriverProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DriverProfile.DoesNotExist:
            return Response({"detail": "Perfil não encontrado."}, status=status.HTTP_404_NOT_FOUND)

# View para logout.
class LogoutApiView(GenericAPIView):
    serializer_class=LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Solicitação de corrida
class CreateRideRequestView(GenericAPIView):
    queryset = RideRequest.objects.all()
    serializer_class = RideRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        passenger = request.user
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        ride_request = serializer.save(passenger=passenger)

        # Calcular a distância usando Haversine
        distance = haversine_distance(
            ride_request.start_location.y, ride_request.start_location.x,
            ride_request.end_location.y, ride_request.end_location.x
        )

        # Calcular o preço da corrida
        price = calculate_price(distance)

        # Atualizar a solicitação de corrida com a distância e o preço
        ride_request.distance = distance
        ride_request.price = price
        ride_request.save()

        # Vincular o motorista mais próximo
        driver_assigned = assign_nearest_driver(ride_request)

        if driver_assigned:
            ride_request.status = 'accepted'
        else:
            ride_request.status = 'pending'
        
        ride_request.save()

        response_data = {
            "message": "Ride request created.",
            "ride_id": ride_request.id,
            "distance": ride_request.distance,
            "price": ride_request.price,
            "status": ride_request.status
        }

        if driver_assigned:
            response_data["driver_id"] = ride_request.driver.id

        return Response(response_data, status=status.HTTP_201_CREATED)

# View para aceitar corrida.
class AcceptRideRequestView(GenericAPIView):
    queryset = RideRequest.objects.all()
    serializer_class = AcceptRideRequestSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        ride_request = self.get_object()
        if ride_request.driver is not None:
            return Response({"error": "This ride has already been accepted by another driver."}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_driver:
            return Response({"error": "Only drivers can accept rides."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(ride_request, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.accept(request.user)
        print("Corrida aceita")
        return Response({"message": "Ride accepted successfully."}, status=status.HTTP_200_OK)

# View para atualizar o local do motorista.
class UpdateDriverLocationView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        driver = request.user
        serializer = DriverLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        location = serializer.validated_data['location']
        
        # Atualiza ou cria a localização do motorista
        DriverLocation.objects.update_or_create(driver=driver, defaults={'location': location})
        
        return Response({"message": "Localização atualizada com sucesso"}, status=status.HTTP_200_OK)

# View para cancelar a corrida passageiro.
class CancelRideByPassengerView(GenericAPIView):
    queryset = RideRequest.objects.all()
    serializer_class = CancelRideRequestSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        ride_request = self.get_object()
        if ride_request.passenger != request.user:
            return Response({"error": "Only the passenger can cancel this ride."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(ride_request, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.cancel_by_passenger()
        print("Cencelado pelo passageiro.")
        return Response({"message": "Ride canceled by passenger."}, status=status.HTTP_200_OK)

# View para status online e off.
class ToggleOnlineStatusView(GenericAPIView):
    serializer_class = ToggleOnlineStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        driver_profile = get_object_or_404(DriverProfile, user_id=user_id)
        return driver_profile

    def patch(self, request, *args, **kwargs):
        driver_profile = self.get_object()
        if not request.user.is_driver:
            return Response({"error": "Apenas motoristas podem alterar o status online."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(driver_profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(f"DriverProfile before update: {driver_profile}")
        print(f"Request data: {request.data}")
        print(f"DriverProfile after update: {driver_profile}")

        return Response({"message": "Status online atualizado com sucesso."}, status=status.HTTP_200_OK)

# View para cancelar corrida motorista.
class CancelRideByDriverView(GenericAPIView):
    queryset = RideRequest.objects.all()
    serializer_class = CancelRideRequestSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        ride_request = self.get_object()
        if ride_request.driver != request.user:
            return Response({"error": "Only the driver can cancel this ride."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(ride_request, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.cancel_by_driver()
        print("Cencelado pelo motorista.")
        return Response({"message": "Ride canceled by driver."}, status=status.HTTP_200_OK)