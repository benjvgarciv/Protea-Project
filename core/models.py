from django.db import models

class Servicio(models.Model):
    codigo = models.CharField(max_length=20, unique=True, primary_key=True)
    categoria = models.CharField(max_length=100)
    titulo = models.CharField(max_length=200)
    resumen = models.TextField()
    detalle = models.TextField()
    encuesta_nombre = models.CharField(max_length=200, blank=True)
    encuesta_preguntas = models.CharField(max_length=200, blank=True)
    duracion = models.CharField(max_length=100)
    modalidad = models.CharField(max_length=100)
    entregables = models.JSONField(default=list)

    def __str__(self):
        return f"[{self.codigo}] {self.titulo}"

class Solicitud(models.Model):
    ESTADOS = (
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Asignado', 'Asignado'),
    )
    ticket = models.CharField(max_length=30, unique=True)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    rut = models.CharField(max_length=20)
    email = models.EmailField()
    telefono = models.CharField(max_length=30)
    organizacion = models.CharField(max_length=200)
    mensaje = models.TextField()
    estado = models.CharField(max_length=30, choices=ESTADOS, default='Pendiente')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket} - {self.organizacion}"

class CarouselImage(models.Model):
    imagen_path = models.CharField(max_length=200) # e.g. "img/team_1.png"
    subtitulo = models.CharField(max_length=200, blank=True, default='NUESTRA TRAYECTORIA & PRESENCIA')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, default='')
    orden = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.orden} - {self.titulo}"
class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.key}: {self.value}"


class EvaluacionEncuesta(models.Model):
    RESULTADOS = (
        ('Apto', 'Apto'),
        ('No Apto', 'No Apto'),
    )
    rut = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    nombre = models.CharField(max_length=200, blank=True)
    timestamp_encuesta = models.CharField(max_length=100, blank=True)
    resultado = models.CharField(max_length=20, choices=RESULTADOS)
    motivo = models.TextField()
    fecha_evaluacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluación de {self.nombre} - {self.resultado}"

