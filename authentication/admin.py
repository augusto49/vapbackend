from django.contrib import admin
from .models import User, OneTimePassword, DriverProfile, PassengerProfile

# Registro dos modelos no admin
admin.site.register(User)
admin.site.register(OneTimePassword)

@admin.register(PassengerProfile)
class PassengerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'cidade', 'cpf', 'data_nascimento')
    list_filter = ('cidade', 'is_active')
    search_fields = ('user__email', 'cpf', 'cidade')
    actions = ['activate_passengers', 'deactivate_passengers']

    def activate_passengers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Passageiro(s) desbloqueado(s) com sucesso.")

    def deactivate_passengers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Passageiro(s) bloqueado(s) com sucesso.")

    activate_passengers.short_description = 'Desbloquear passageiros selecionados'
    deactivate_passengers.short_description = 'Bloquear passageiros selecionados'
    
# Configuração do admin para DriverProfile
@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'cidade', 'cpf', 'data_nascimento')
    list_filter = ('status', 'cidade')
    search_fields = ('user__email', 'cpf', 'cidade')
    actions = ['approve_drivers', 'reject_drivers']

    def approve_drivers(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, "Motorista(s) aprovado(s) com sucesso.")

    def reject_drivers(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Motorista(s) rejeitado(s) com sucesso.")
        
    def activate_drivers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Motorista(s) desbloqueado(s) com sucesso.")

    def deactivate_drivers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Motorista(s) bloqueado(s) com sucesso.")

    approve_drivers.short_description = 'Aprovar motoristas selecionados'
    reject_drivers.short_description = 'Rejeitar motoristas selecionados'
