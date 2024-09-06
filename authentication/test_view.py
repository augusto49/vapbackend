from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.gis.geos import Point
from authentication.models import DriverLocation, DriverProfile, User, PassengerProfile, RideRequest

# Teste de solicitação
class RideRequestTests(APITestCase):
    def setUp(self):
        self.passenger_user = User.objects.create_user(
            email='passenger@example.com', 
            password='pass1234', 
            first_name='John', 
            last_name='Doe', 
            is_passenger=True, 
            is_verified=True
        )
        self.passenger_profile = PassengerProfile.objects.create(
            user=self.passenger_user, 
            cidade='City',
            telefone='123456789',
            cpf='12345678901',
            data_nascimento=date(1990, 1, 1),
            genero='M',
            termo_aceite=True
        )

        self.driver_user = User.objects.create_user(
            email='driver@example.com', 
            password='driver1234', 
            first_name='Jane', 
            last_name='Smith', 
            is_driver=True, 
            is_verified=True
        )
        self.driver_profile = DriverProfile.objects.create(
            user=self.driver_user,
            cidade='City',
            telefone='987654321',
            cpf='09876543210',
            data_nascimento=date(1985, 5, 20),
            genero='F',
            status='approved',
            termo_aceite=True,
            cep='12345678',
            endereco='Rua Exemplo',
            numero='123',
            bairro='Bairro Exemplo',
            uf='SP',
            modelo_veiculo='Toyota Corolla',
            ano_veiculo=2020,
            cor_veiculo='Branco',
            placa_veiculo='ABC1234',
            is_online=True  # Motorista online
        )
        
         # Adiciona a localização do motorista
        self.driver_location = DriverLocation.objects.create(
            driver=self.driver_user,
            location=Point(-46.57421, -21.785741, srid=4326)
        )

        self.client.force_authenticate(user=self.passenger_user)
        self.ride_request_url = reverse('create-ride-request')

    def test_create_ride_request(self):
        start_location = {'type': 'Point', 'coordinates': [-46.57421, -21.785741]}
        end_location = {'type': 'Point', 'coordinates': [-46.57422, -21.785742]}
        data = {
            'start_location': start_location,
            'end_location': end_location
        }

        response = self.client.post(self.ride_request_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RideRequest.objects.count(), 1)
        
        ride_request = RideRequest.objects.first()
        self.assertEqual(ride_request.passenger, self.passenger_user)
        self.assertIsNotNone(ride_request.distance)
        self.assertIsNotNone(ride_request.price)
        self.assertIsNotNone(ride_request.driver)  # Verifique se o motorista foi atribuído
        self.assertEqual(ride_request.driver, self.driver_user)
        self.assertEqual(ride_request.status, 'accepted' if ride_request.driver else 'pending')

# Teste online e off
class ToggleOnlineStatusTests(APITestCase):
    def setUp(self):
        # Configurar dados iniciais para Motorista
        self.driver_user = User.objects.create_user(
            email='driver@example.com', 
            password='driver1234', 
            first_name='Jane', 
            last_name='Smith', 
            is_driver=True, 
            is_verified=True
        )

        self.driver_profile = DriverProfile.objects.create(
            user=self.driver_user,
            cidade='City',
            telefone='987654321',
            cpf='09876543210',
            data_nascimento=date(1985, 5, 20),  # Adicionado data de nascimento
            genero='F',
            status='approved',
            termo_aceite=True,
            cep='12345678',
            endereco='Rua Exemplo',
            numero='123',
            bairro='Bairro Exemplo',
            uf='SP',
            modelo_veiculo='Toyota Corolla',
            ano_veiculo=2020,
            cor_veiculo='Branco',
            placa_veiculo='ABC1234',
        )

        self.client.force_authenticate(user=self.driver_user)
        self.toggle_online_status_url = reverse('toggle-online-status', kwargs={'pk': self.driver_profile.pk})

    def test_toggle_online_status(self):
        # Testar mudar o status para online
        response = self.client.patch(self.toggle_online_status_url, {'is_online': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.driver_profile.refresh_from_db()
        self.assertTrue(self.driver_profile.is_online)

        # Testar mudar o status para offline
        response = self.client.patch(self.toggle_online_status_url, {'is_online': False}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.driver_profile.refresh_from_db()
        self.assertFalse(self.driver_profile.is_online)
        
# Teste de aceitar corrida
class AcceptRideRequestTests(APITestCase):
    def setUp(self):
        # Configurar dados iniciais para Passageiro
        self.passenger_user = User.objects.create_user(
            email='passenger@example.com', 
            password='pass1234', 
            first_name='John', 
            last_name='Doe', 
            is_passenger=True, 
            is_verified=True
        )
        
        self.passenger_profile = PassengerProfile.objects.create(
            user=self.passenger_user, 
            cidade='City',
            telefone='123456789',
            cpf='12345678901',
            data_nascimento=date(1990, 1, 1),  # Adicionado data de nascimento
            genero='M',
            termo_aceite=True
        )

        # Configurar dados iniciais para Motorista
        self.driver_user = User.objects.create_user(
            email='driver@example.com', 
            password='driver1234', 
            first_name='Jane', 
            last_name='Smith', 
            is_driver=True, 
            is_verified=True
        )

        self.driver_profile = DriverProfile.objects.create(
            user=self.driver_user,
            cidade='City',
            telefone='987654321',
            cpf='09876543210',
            data_nascimento=date(1985, 5, 20),  # Adicionado data de nascimento
            genero='F',
            status='approved',
            termo_aceite=True,
            # Adicione todos os campos obrigatórios do modelo DriverProfile
            cep='12345678',
            endereco='Rua Exemplo',
            numero='123',
            bairro='Bairro Exemplo',
            uf='SP',
            modelo_veiculo='Toyota Corolla',
            ano_veiculo=2020,  # Campo adicionado para evitar erro de valor nulo
            cor_veiculo='Branco',
            placa_veiculo='ABC1234',
        )

        # Criar uma corrida pendente para ser aceita pelo motorista
        self.ride_request = RideRequest.objects.create(
            passenger=self.passenger_user,
            start_location=Point(-46.57421, -21.785741, srid=4326),
            end_location=Point(-46.57422, -21.785742, srid=4326),
            status='pending'
        )

        self.client.force_authenticate(user=self.driver_user)
        self.accept_ride_url = reverse('accept-ride', kwargs={'pk': self.ride_request.pk})

    def test_accept_ride(self):
        # Teste para o motorista aceitar a corrida
        response = self.client.patch(self.accept_ride_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride_request.refresh_from_db()
        self.assertEqual(self.ride_request.status, 'accepted')
        self.assertEqual(self.ride_request.driver, self.driver_user)

# Teste de cancelamento passageiro
class RideRequestCancelTests(APITestCase):
    def setUp(self):
        # Configurar dados iniciais para Passageiro
        self.passenger_user = User.objects.create_user(
            email='passenger@example.com', 
            password='pass1234', 
            first_name='John', 
            last_name='Doe', 
            is_passenger=True, 
            is_verified=True
        )
        
        self.passenger_profile = PassengerProfile.objects.create(
            user=self.passenger_user, 
            cidade='City',
            telefone='123456789',
            cpf='12345678901',
            data_nascimento=date(1990, 1, 1),  
            genero='M',
            termo_aceite=True
        )

        # Configurar dados iniciais para Motorista
        self.driver_user = User.objects.create_user(
            email='driver@example.com', 
            password='driver1234', 
            first_name='Jane', 
            last_name='Smith', 
            is_driver=True, 
            is_verified=True
        )

        self.driver_profile = DriverProfile.objects.create(
            user=self.driver_user,
            cidade='City',
            telefone='987654321',
            cpf='09876543210',
            data_nascimento=date(1985, 5, 20),  
            genero='F',
            ano_veiculo=2020,
            status='approved',
            termo_aceite=True
        )

        self.client.force_authenticate(user=self.passenger_user)

        # Criar uma corrida para cancelar
        self.ride_request = RideRequest.objects.create(
            passenger=self.passenger_user,
            start_location=Point(-46.57421, -21.785741, srid=4326),
            end_location=Point(-46.57422, -21.785742, srid=4326),
            status='pending'
        )
        self.cancel_ride_url = reverse('cancel-ride-passenger', kwargs={'pk': self.ride_request.pk})

    def test_cancel_ride_by_passenger(self):
        # Teste para cancelar a corrida
        response = self.client.patch(self.cancel_ride_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride_request.refresh_from_db()
        self.assertEqual(self.ride_request.status, 'canceled')
        self.assertEqual(self.ride_request.canceled_by, 'passenger')

# Teste de cancelamento motorista
class RideRequestCancelByDriverTests(APITestCase):
    def setUp(self):
        # Configurar dados iniciais para Passageiro
        self.passenger_user = User.objects.create_user(
            email='passenger@example.com', 
            password='pass1234', 
            first_name='John', 
            last_name='Doe', 
            is_passenger=True, 
            is_verified=True
        )
        
        self.passenger_profile = PassengerProfile.objects.create(
            user=self.passenger_user, 
            cidade='City',
            telefone='123456789',
            cpf='12345678901',
            data_nascimento=date(1990, 1, 1),  
            genero='M',
            termo_aceite=True
        )

        # Configurar dados iniciais para Motorista
        self.driver_user = User.objects.create_user(
            email='driver@example.com', 
            password='driver1234', 
            first_name='Jane', 
            last_name='Smith', 
            is_driver=True, 
            is_verified=True
        )

        self.driver_profile = DriverProfile.objects.create(
            user=self.driver_user,
            cidade='City',
            telefone='987654321',
            cpf='09876543210',
            data_nascimento=date(1985, 5, 20),  
            genero='F',
            ano_veiculo=2020,
            status='approved',
            termo_aceite=True
        )

        # Criar uma corrida para ser cancelada pelo motorista
        self.ride_request = RideRequest.objects.create(
            passenger=self.passenger_user,
            driver=self.driver_user,
            start_location=Point(-46.57421, -21.785741, srid=4326),
            end_location=Point(-46.57422, -21.785742, srid=4326),
            status='accepted'
        )

        self.client.force_authenticate(user=self.driver_user)
        self.cancel_ride_url = reverse('cancel-ride-driver', kwargs={'pk': self.ride_request.pk})

    def test_cancel_ride_by_driver(self):
        # Teste para o motorista cancelar a corrida
        response = self.client.patch(self.cancel_ride_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride_request.refresh_from_db()
        self.assertEqual(self.ride_request.status, 'canceled')
        self.assertEqual(self.ride_request.canceled_by, 'driver')
