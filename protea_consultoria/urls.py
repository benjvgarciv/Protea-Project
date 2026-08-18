from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('servicios/', views.servicios, name='servicios'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('contacto/', views.contacto, name='contacto'),
    path('solicitud/', views.solicitud, name='solicitud'),
    path('solicitud/exito/', views.solicitud_exito, name='solicitud_exito'),
    path('login/', views.login_view, name='login'),
    path('login/recuperar/', views.recuperar_password_view, name='recuperar_password'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/respuesta/<int:id>/', views.admin_survey_detail, name='survey_detail'),
    path('dashboard/certificado/<str:cert_id>/', views.descargar_certificado_pdf, name='descargar_certificado'),
    path('dashboard/servicio/crear/', views.admin_servicio_crear, name='servicio_crear'),
    path('dashboard/servicio/editar/<str:codigo>/', views.admin_servicio_editar, name='servicio_editar'),
    path('dashboard/servicio/eliminar/<str:codigo>/', views.admin_servicio_eliminar, name='servicio_eliminar'),
    path('dashboard/solicitud/editar/<int:id>/', views.admin_solicitud_editar, name='solicitud_editar'),
    path('dashboard/solicitud/eliminar/<int:id>/', views.admin_solicitud_eliminar, name='solicitud_eliminar'),
    path('dashboard/carrusel/crear/', views.admin_carousel_crear, name='carousel_crear'),
    path('dashboard/carrusel/editar/<int:id>/', views.admin_carousel_editar, name='carousel_editar'),
    path('dashboard/carrusel/eliminar/<int:id>/', views.admin_carousel_eliminar, name='carousel_eliminar'),
]
