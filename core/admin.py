from django.contrib import admin
from .models import Servicio, Solicitud, CarouselImage

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'categoria', 'titulo', 'duracion', 'modalidad')
    search_fields = ('codigo', 'titulo', 'categoria')

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'organizacion', 'servicio', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('ticket', 'organizacion', 'nombre', 'rut')

@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ('orden', 'titulo', 'imagen_path')
    search_fields = ('titulo', 'imagen_path')
