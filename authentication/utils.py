import math
from django.core.mail import EmailMessage
import random
from django.conf import settings
import requests
from .models import DriverLocation, User, OneTimePassword
from django.contrib.sites.shortcuts import get_current_site

# Envio generativo de otp email
def send_generated_otp_to_email(email, request): 
    subject = "One time passcode for Email verification"
    otp = random.randint(100000, 999999) 
    current_site=get_current_site(request).domain
    user = User.objects.get(email=email)
    email_body=f"Hi {user.first_name} thanks for signing up on {current_site} please verify your email with the \n one time passcode {otp}"
    from_email=settings.DEFAULT_FROM_EMAIL
    otp_obj=OneTimePassword.objects.create(user=user, otp=otp)
    #send the email 
    d_email=EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[user.email])
    d_email.send()

# Envio para email
def send_normal_email(data):
    email=EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()

# Função para vincular o motorista mais próximo à solicitação de corrida
def assign_nearest_driver(ride_request):
    start_location = ride_request.start_location
    # Filtra motoristas online
    available_drivers = DriverLocation.objects.filter(driver__driverprofile__is_online=True)

    nearest_driver = None
    min_distance = float('inf')

    for driver_location in available_drivers:
        driver_point = driver_location.location
        distance = ride_request.distance  # Usa a distância já calculada e enviada pelo front-end

        if distance < min_distance:
            min_distance = distance
            nearest_driver = driver_location.driver

    if nearest_driver:
        # Atribui o motorista mais próximo à solicitação de corrida
        ride_request.driver = nearest_driver
        ride_request.status = 'accepted'
        ride_request.save()
        return nearest_driver
    else:
        print("Nenhum motorista disponível nas proximidades.")
        return None

# Função para fazer a requisição à API do Google Maps e calcular a rota
def get_route_from_google_maps(origin, destination):
    api_key = settings.GOOGLE_MAPS_API_KEY
    base_url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        'origin': f"{origin['lat']},{origin['lng']}",
        'destination': f"{destination['lat']},{destination['lng']}",
        'key': api_key,
        'mode': 'driving'
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()

        if data['status'] == 'OK':
            # Extrair a distância e o tempo da primeira rota
            route = data['routes'][0]['legs'][0]
            distance_km = route['distance']['value'] / 1000  # Converter metros para quilômetros
            duration_minutes = route['duration']['value'] / 60  # Converter segundos para minutos

            return {
                'distance_km': distance_km,
                'duration_minutes': duration_minutes,
                'route': data['routes'][0]  # Retorna a rota completa
            }
        else:
            raise Exception(f"Erro na API do Google Maps: {data['status']}")
    else:
        raise Exception(f"Erro ao conectar com a API do Google Maps: {response.status_code}")

# Função para calcular o preço baseado na distância
def calculate_price(distance_km):
    base_fare = 5.00  # Tarifa base
    cost_per_km = 2.50  # Custo por quilômetro
    return base_fare + (cost_per_km * distance_km)
