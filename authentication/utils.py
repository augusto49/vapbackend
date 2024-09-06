import math
from django.core.mail import EmailMessage
import random
from django.conf import settings
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

# encontrar motorista
def assign_nearest_driver(ride_request):
    start_location = ride_request.start_location
    available_drivers = DriverLocation.objects.filter(driver__driverprofile__is_online=True)

    nearest_driver = None
    min_distance = None

    for driver_location in available_drivers:
        driver_point = driver_location.location
        distance = haversine_distance(
            start_location.y, start_location.x,
            driver_point.y, driver_point.x
        )

        if min_distance is None or distance < min_distance:
            min_distance = distance
            nearest_driver = driver_location.driver

    if nearest_driver:
        ride_request.driver = nearest_driver
        ride_request.status = 'accepted'
        ride_request.distance = min_distance  # Armazena a distância calculada
        ride_request.price = calculate_price(min_distance)  # Calcula o preço baseado na distância
        ride_request.save()
        return True  # Indica que um motorista foi atribuído
    else:
        print("Nenhum motorista disponível nas proximidades.")

# calculo de distancia
def haversine_distance(lat1, lon1, lat2, lon2):
    # Conversão de graus para radianos
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Fórmula de Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Raio da Terra em quilômetros
    r = 6371
    return c * r

# calculo preço
def calculate_price(distance):
    base_fare = 5.00  # Tarifa base
    cost_per_km = 2.50  # Custo por quilômetro
    return base_fare + (cost_per_km * distance)
