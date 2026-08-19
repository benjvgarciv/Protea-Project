from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .models import Servicio, Solicitud, CarouselImage, SystemSetting, EvaluacionEncuesta
from django.core.mail import send_mail
import random
import os
import time
import csv
import urllib.request
import io
from django.conf import settings

DEFAULT_SERVICIOS = [
    {
        "codigo": "GP-01",
        "categoria": "Gestión de Personas",
        "titulo": "Gestión de Personas y Reclutamiento Activo",
        "resumen": "Selección especializada y evaluaciones psicolaborales para cargos técnicos y de alta responsabilidad en el sector industrial y corporativo.",
        "detalle": "Enfoque especializado en la zona centro-sur de Chile. Incluye reclutamiento técnico, evaluaciones psicolaborales estándar e institucionales (normativa Corma) y test de aversión al riesgo.",
        "encuesta_nombre": "Test de Aversión al Riesgo & Evaluaciones Psicolaborales",
        "encuesta_preguntas": "Evaluaciones a medida",
        "duracion": "A medida según requerimiento",
        "modalidad": "Presencial / Online",
        "entregables": [
            "Reclutamiento y selección de perfiles técnicos e industriales",
            "Evaluaciones psicolaborales completas y acreditación Corma",
            "Aplicación de test de aversión al riesgo para operarios críticos",
            "Informes de idoneidad y reportes de compatibilidad de cargo"
        ]
    },
    {
        "codigo": "OTEC-02",
        "categoria": "Capacitación & Formación",
        "titulo": "Capacitación y Formación Laboral Adaptativa (OTEC)",
        "resumen": "Programas prácticos de capacitación diseñados bajo metodología adaptativa para conformar equipos resilientes en entornos de alta incertidumbre.",
        "detalle": "Talleres in-company y cursos prácticos enfocados en el desarrollo de competencias blandas, alineación estratégica y resolución colaborativa de conflictos.",
        "encuesta_nombre": "Detección de Necesidades de Capacitación (DNC)",
        "encuesta_preguntas": "Talleres personalizados",
        "duracion": "Cursos modulares flexibles",
        "modalidad": "In-company / Virtual",
        "entregables": [
            "Capacitación oficial certificada bajo Norma de Calidad OTEC",
            "Talleres prácticos de trabajo en equipo y comunicación asertiva",
            "Sesiones de desarrollo de liderazgo directivo y toma de decisiones",
            "Manuales de contenidos y planes de aplicación post-capacitación"
        ]
    },
    {
        "codigo": "SO-03",
        "categoria": "Salud Ocupacional & Clima",
        "titulo": "Salud Ocupacional y Diagnósticos de Clima",
        "resumen": "Medición de riesgos psicosociales y programas de psicología preventiva para mitigar el estrés y la fatiga laboral.",
        "detalle": "Asesoría técnica completa para dar cumplimiento a la normativa chilena sobre riesgos psicosociales, promoviendo espacios de salud mental sostenibles.",
        "encuesta_nombre": "Cuestionario de Evaluación de Riesgos Psicosociales",
        "encuesta_preguntas": "Cuestionario estandarizado",
        "duracion": "4 a 6 semanas",
        "modalidad": "Online / Mixta",
        "entregables": [
            "Aplicación e informe completo de Protocolo Psicosocial según ley chilena",
            "Diagnóstico de clima organizacional y mapa de riesgos psicosociales",
            "Talleres de psicología preventiva para mitigar estrés laboral y fatiga",
            "Plan de acción para comités paritarios y gerencias de recursos humanos"
        ]
    }
]

ETAPAS = [
    {
        "numero": "01",
        "nombre": "Raíz",
        "titulo": "Diagnóstico",
        "descripcion": "Entendemos el terreno real: datos, cultura, mercado y "
                        "restricciones. Sin diagnóstico honesto no hay estrategia "
                        "que funcione.",
    },
    {
        "numero": "02",
        "nombre": "Fuego",
        "titulo": "Diseño",
        "descripcion": "Como muchas proteáceas, una estrategia útil también nace "
                        "de decisiones difíciles. Diseñamos el camino que exige "
                        "soltar lo que ya no sirve.",
    },
    {
        "numero": "03",
        "nombre": "Floración",
        "titulo": "Implementación",
        "descripcion": "Acompañamos la ejecución y dejamos capacidad instalada "
                        "para que el resultado se sostenga sin nosotros.",
    },
]

CIFRAS = [
    {"valor": "11", "etiqueta": "años de trayectoria"},
    {"valor": "15", "etiqueta": "organizaciones asesoradas"},
    {"valor": "6", "etiqueta": "países en la región"},
    {"valor": "94%", "etiqueta": "clientes que continúan con nosotros"},
]

VALORES = [
    {
        "nombre": "Raíz antes que ramas",
        "descripcion": "No recomendamos nada que no entendamos desde la base del negocio.",
    },
    {
        "nombre": "Resiliencia con propósito",
        "descripcion": "Diseñamos estrategias pensadas para resistir ciclos difíciles, no solo para el mejor escenario.",
    },
    {
        "nombre": "Transferencia real",
        "descripcion": "Medimos el éxito por lo que el equipo puede sostener después que nos vamos.",
    },
]

EQUIPO = [
    {
        "nombre": "Gabriela Bahamondes Valenzuela",
        "rol": "Fundadora y Directora — Psicóloga Organizacional",
        "origen": "Universidad de Concepción",
        "experiencia": "14+ años de experiencia",
        "descripcion": "Fundadora y líder de Consultora Protea. Especialista en psicología del trabajo, desarrollo de equipos y gestión de personas con amplia trayectoria en el sector industrial de la zona centro-sur.",
        "foto": "img/team_1.png",
    },
    {
        "nombre": "Rodrigo Silva",
        "rol": "Consultor Senior en Transformación",
        "origen": "Pontificia Universidad Católica de Chile",
        "experiencia": "12+ años de experiencia",
        "descripcion": "Líder en arquitectura organizacional, optimización de procesos y acompañamiento directivo.",
        "foto": "img/team_2.png",
    },
    {
        "nombre": "Camila Morales",
        "rol": "Especialista en Finanzas & Gobernanza",
        "origen": "Universidad de Chile",
        "experiencia": "10+ años de experiencia",
        "descripcion": "Experta en modelos financieros, gestión integral de riesgos y criterios ASG / gobernanza.",
        "foto": "img/team_3.png",
    },
]


OPINIONES = [
    {
        "autor": "Sergio",
        "estrellas": 4,
        "tiempo": "Hace 5 meses",
        "texto": "La charla resultó interesante. Ejemplificando situaciones rutinarias y vivenciales de emociones que uno vive a diario dentro del aula. Lo que sí, me costó poder seguirle la idea completa ya que explicaba sin sintetizar al hablar."
    },
    {
        "autor": "Carlo Sari",
        "estrellas": 5,
        "tiempo": "Hace 1 mes",
        "texto": "Muy buena charla y con muchos tips para usar diariamente. Gracias Iñaki."
    },
    {
        "autor": "Ismael Esparza",
        "estrellas": 5,
        "tiempo": "Hace 2 meses",
        "texto": "Buena capacitación, clara, detallada, coherente muchas gracias."
    },
    {
        "autor": "Sofía Meier",
        "estrellas": 5,
        "tiempo": "Hace 3 meses",
        "texto": "Buenísima capacitación. Ideal para quienes estamos partiendo trabajando en Salud 😁…"
    },
    {
        "autor": "Paola Andrea Lara Polanco",
        "estrellas": 4,
        "tiempo": "Hace 1 mes",
        "texto": "Excelente charla, pero siempre cuando hay charlas con temas tan interesantes se hace corto el tiempo para abordar más variables."
    }
]


def seed_default_services_if_empty():
    if not Servicio.objects.exists():
        for s in DEFAULT_SERVICIOS:
            Servicio.objects.create(
                codigo=s['codigo'],
                categoria=s['categoria'],
                titulo=s['titulo'],
                resumen=s['resumen'],
                detalle=s['detalle'],
                encuesta_nombre=s.get('encuesta_nombre', ''),
                encuesta_preguntas=s.get('encuesta_preguntas', ''),
                duracion=s['duracion'],
                modalidad=s['modalidad'],
                entregables=s['entregables']
            )


def seed_default_carousel_if_empty():
    if not CarouselImage.objects.exists():
        default_slides = [
            {"imagen_path": "img/team_1.png", "subtitulo": "Dirección & Liderazgo", "titulo": "Gabriela Bahamondes", "descripcion": "Psicóloga organizacional, consultora y Directora en Protea Consultoría, liderando procesos de diagnóstico y OTEC.", "orden": 0},
            {"imagen_path": "img/team_2.png", "subtitulo": "Estrategia Organizacional", "titulo": "Consultoría Estratégica", "descripcion": "Diseñamos soluciones aplicadas para potenciar el capital humano y optimizar el desarrollo interno.", "orden": 1},
            {"imagen_path": "img/team_3.png", "subtitulo": "Clima & Bienestar", "titulo": "Salud Ocupacional y Clima", "descripcion": "Apoyamos en la mejora del clima laboral, la resiliencia organizacional y el bienestar laboral general.", "orden": 2},
            {"imagen_path": "img/workshop.jpg", "subtitulo": "Capacitación Certificada (OTEC)", "titulo": "Talleres y Capacitación Laboral", "descripcion": "Realizamos talleres interactivos, dinámicas y entrenamientos certificados para desarrollar competencias.", "orden": 3},
        ]
        for i, s in enumerate(default_slides):
            CarouselImage.objects.create(
                imagen_path=s["imagen_path"],
                subtitulo=s["subtitulo"],
                titulo=s["titulo"],
                descripcion=s["descripcion"],
                orden=s["orden"]
            )


def inicio(request):
    seed_default_services_if_empty()
    seed_default_carousel_if_empty()
    servicios_list = Servicio.objects.all()[:4]
    carousel_list = CarouselImage.objects.all().order_by('orden')[:5]
    contexto = {
        "servicios": servicios_list,
        "carousel": carousel_list,
        "cifras": cifras_list if 'cifras_list' in locals() else CIFRAS,
        "opiniones": opiniones_list if 'opiniones_list' in locals() else OPINIONES,
        "activo": "inicio",
    }
    return render(request, "core/inicio.html", contexto)


def servicios(request):
    seed_default_services_if_empty()
    
    query = request.GET.get('q', '').strip()
    categoria_selected = request.GET.get('categoria', '').strip()
    
    # Obtener todas las categorías únicas para los filtros
    categorias = Servicio.objects.values_list('categoria', flat=True).distinct()
    
    # Filtrar QuerySet
    servicios_queryset = Servicio.objects.all().order_by('codigo')
    
    if query:
        from django.db.models import Q
        servicios_queryset = servicios_queryset.filter(
            Q(titulo__icontains=query) |
            Q(resumen__icontains=query) |
            Q(detalle__icontains=query) |
            Q(codigo__icontains=query)
        )
        
    if categoria_selected:
        servicios_queryset = servicios_queryset.filter(categoria=categoria_selected)
        
    # Paginación (3 servicios por página)
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(servicios_queryset, 3)
    page_number = request.GET.get('page')
    
    try:
        servicios_paginados = paginator.page(page_number)
    except PageNotAnInteger:
        servicios_paginados = paginator.page(1)
    except EmptyPage:
        servicios_paginados = paginator.page(paginator.num_pages)
        
    contexto = {
        "servicios": servicios_paginados,
        "categorias": categorias,
        "query": query,
        "categoria_selected": categoria_selected,
        "activo": "servicios"
    }
    return render(request, "core/servicios.html", contexto)


def nosotros(request):
    contexto = {
        "valores": VALORES,
        "equipo": EQUIPO,
        "cifras": CIFRAS,
        "activo": "nosotros",
    }
    return render(request, "core/nosotros.html", contexto)


def contacto(request):
    return render(request, "core/contacto.html", {"activo": "contacto"})


def solicitud(request):
    seed_default_services_if_empty()
    
    # Si es POST, registramos la solicitud en BD
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        rut = request.POST.get('rut')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        organizacion = request.POST.get('organizacion')
        mensaje = request.POST.get('mensaje')
        servicio_codigo = request.POST.get('servicio_id')
        
        try:
            servicio_obj = Servicio.objects.get(codigo=servicio_codigo)
        except Servicio.DoesNotExist:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'error': 'Servicio seleccionado no válido.'})
            
        # Generar ticket
        ticket_id = f"#PR-2026-{random.randint(1000, 9999)}"
        while Solicitud.objects.filter(ticket=ticket_id).exists():
            ticket_id = f"#PR-2026-{random.randint(1000, 9999)}"
            
        solicitud_obj = Solicitud.objects.create(
            ticket=ticket_id,
            servicio=servicio_obj,
            nombre=nombre,
            rut=rut,
            email=email,
            telefono=telefono,
            organizacion=organizacion,
            mensaje=mensaje,
            estado="Pendiente"
        )
        
        from django.http import JsonResponse
        return JsonResponse({
            'success': True,
            'ticket': solicitud_obj.ticket,
            'servicio_titulo': servicio_obj.titulo,
            'organizacion': solicitud_obj.organizacion,
            'email': solicitud_obj.email
        })
        
    # Si es GET, cargamos el formulario
    codigo_seleccionado = request.GET.get('servicio', 'GP-01')
    servicios_list = Servicio.objects.all()
    
    servicio_seleccionado = servicios_list.filter(codigo=codigo_seleccionado).first()
    if not servicio_seleccionado and servicios_list.exists():
        servicio_seleccionado = servicios_list.first()
        
    contexto = {
        "servicios": servicios_list,
        "seleccionado": servicio_seleccionado,
        "activo": "solicitud"
    }
    return render(request, "core/solicitud.html", contexto)


@never_cache
def login_view(request):
    # Asegurar que el usuario de prueba existe para facilitar la validación
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        
    if not User.objects.filter(username='usuario').exists():
        User.objects.create_user('usuario', 'usuario@example.com', 'usuario123')
        
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        usuario = request.POST.get('username', '').strip()
        clave = request.POST.get('password')
        
        # Intentar autenticar con el usuario ingresado directamente
        user = authenticate(request, username=usuario, password=clave)
        
        # Si falla, intentar normalizar el RUT (quitar puntos) para ver si coincide
        if user is None:
            normalized_username = usuario.replace('.', '')
            user = authenticate(request, username=normalized_username, password=clave)
            
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            
    return render(request, 'core/login.html', {'activo': 'login'})


@never_cache
def recuperar_password_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        messages.success(
            request,
            "Si el RUT o correo ingresado está registrado, "
            "recibirás un correo con las instrucciones para restablecer tu contraseña a la brevedad."
        )
        return render(request, 'core/recuperar_password.html', {'activo': 'login', 'enviado': True})
        
    return render(request, 'core/recuperar_password.html', {'activo': 'login', 'enviado': False})


@never_cache
@login_required(login_url='login')
def admin_survey_detail(request, id):
    # Obtener la url de google sheets
    google_sheet_url_setting = SystemSetting.objects.filter(key='google_sheet_url').first()
    google_sheet_url = google_sheet_url_setting.value if google_sheet_url_setting else ''
    
    survey_responses = []
    if google_sheet_url:
        headers, survey_responses, survey_error = fetch_and_parse_google_sheet(google_sheet_url)
    else:
        survey_responses = MOCK_SURVEY_RESPONSES
        
    # Buscar la respuesta por el ID dado
    response_obj = None
    for resp in survey_responses:
        if int(resp['id']) == int(id):
            response_obj = resp
            break
            
    if not response_obj:
        from django.http import Http404
        raise Http404("La respuesta de encuesta no fue encontrada.")
        
    # Buscar si ya existe una evaluación previa para esta persona
    evaluacion = EvaluacionEncuesta.objects.filter(
        rut=response_obj.get('rut', ''),
        email=response_obj.get('email', ''),
        timestamp_encuesta=response_obj.get('timestamp', '')
    ).first()
    
    if request.method == 'POST':
        resultado = request.POST.get('resultado')
        motivo = request.POST.get('motivo', '').strip()
        
        if not evaluacion:
            evaluacion = EvaluacionEncuesta(
                rut=response_obj.get('rut', ''),
                email=response_obj.get('email', ''),
                nombre=response_obj.get('nombre', 'Sin Nombre'),
                timestamp_encuesta=response_obj.get('timestamp', '')
            )
        evaluacion.resultado = resultado
        evaluacion.motivo = motivo
        evaluacion.save()
        
        # Intentar enviar el correo al correo del encuestado si existe
        email_enviado = False
        destinatario = response_obj.get('email', '').strip()
        if destinatario:
            try:
                # Obtener el remitente desde la configuración del mailer
                remitente = 'b5d2bf001@smtp-brevo.com'
                if hasattr(settings, 'MAILERS') and 'default' in settings.MAILERS:
                    options = settings.MAILERS['default'].get('OPTIONS', {})
                    remitente = options.get('username', remitente)
                elif hasattr(settings, 'DEFAULT_FROM_EMAIL'):
                    remitente = settings.DEFAULT_FROM_EMAIL
                
                asunto = "Evaluación de Perfil Psicolaboral - Protea Consultoría"
                mensaje = (
                    f"Estimado/a {response_obj.get('nombre', 'Candidato')}:\n\n"
                    f"Esperamos que te encuentres muy bien.\n\n"
                    f"Te escribimos de Protea Consultoría para notificarte que hemos evaluado las respuestas "
                    f"que ingresaste en nuestra encuesta de diagnóstico el {response_obj.get('timestamp', '')}.\n\n"
                    f"--------------------------------------------------\n"
                    f"Resultado de la evaluación: {resultado}\n"
                    f"--------------------------------------------------\n\n"
                    f"Comentarios y Observaciones de nuestros consultores:\n"
                    f"{motivo}\n\n"
                    f"Agradecemos enormemente tu tiempo y participación en este proceso.\n\n"
                    f"Atentamente,\n"
                    f"Equipo de Protea Consultoría"
                )
                
                send_mail(
                    asunto,
                    mensaje,
                    remitente,
                    [destinatario],
                    fail_silently=False
                )
                email_enviado = True
            except Exception as e:
                messages.error(request, f"Se guardó la calificación, pero no se pudo enviar el correo de notificación: {e}")
                
        if email_enviado:
            messages.success(request, f"Calificación registrada con éxito. Se envió un correo de notificación a {destinatario}.")
        elif not destinatario:
            messages.success(request, "Calificación registrada con éxito. (No se pudo enviar correo porque no se especificó dirección).")
            
        return redirect('survey_detail', id=id)
        
    contexto = {
        'activo': 'dashboard',
        'response': response_obj,
        'evaluacion': evaluacion
    }
    return render(request, 'core/survey_detail.html', contexto)



def logout_view(request):
    logout(request)
    return redirect('inicio')


def fetch_and_parse_google_sheet(csv_url):
    try:
        req = urllib.request.Request(
            csv_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            csv_data = response.read().decode('utf-8')
            
        reader = csv.reader(io.StringIO(csv_data))
        rows = list(reader)
        if not rows:
            return [], [], "El archivo CSV está vacío."
            
        headers = rows[0]
        data_rows = rows[1:]
        
        email_idx = -1
        nombre_idx = -1
        rut_idx = -1
        
        for idx, h in enumerate(headers):
            h_lower = h.lower()
            if email_idx == -1 and ('correo' in h_lower or 'email' in h_lower or 'mail' in h_lower):
                email_idx = idx
            elif nombre_idx == -1 and ('nombre' in h_lower or 'contacto' in h_lower or 'solicitante' in h_lower):
                nombre_idx = idx
            elif rut_idx == -1 and 'rut' in h_lower:
                rut_idx = idx
                
        parsed_rows = []
        for r_num, row in enumerate(data_rows):
            if not row or len(row) < len(headers):
                continue
                
            timestamp = row[0] if len(row) > 0 else ''
            email = row[email_idx] if email_idx != -1 and len(row) > email_idx else ''
            nombre = row[nombre_idx] if nombre_idx != -1 and len(row) > nombre_idx else ''
            rut = row[rut_idx] if rut_idx != -1 and len(row) > rut_idx else ''
            
            questions_answers = []
            for col_idx, col_val in enumerate(row):
                questions_answers.append({
                    'pregunta': headers[col_idx],
                    'respuesta': col_val
                })
                
            parsed_rows.append({
                'id': r_num + 1,
                'timestamp': timestamp,
                'email': email,
                'nombre': nombre,
                'rut': rut,
                'detalle': questions_answers
            })
            
        return headers, parsed_rows, None
        
    except Exception as e:
        return [], [], f"Error al procesar la hoja de cálculo: {str(e)}"

MOCK_SURVEY_RESPONSES = [
    {
        'id': 1,
        'timestamp': "14/08/2026 15:32:11",
        'email': "j.valenzuela@arauco.cl",
        'nombre': "Jaime Valenzuela Soto",
        'rut': "15.482.912-3",
        'detalle': [
            {'pregunta': "Marca temporal", 'respuesta': "14/08/2026 15:32:11"},
            {'pregunta': "Nombre Completo", 'respuesta': "Jaime Valenzuela Soto"},
            {'pregunta': "RUT", 'respuesta': "15.482.912-3"},
            {'pregunta': "Correo Electrónico Corporativo", 'respuesta': "j.valenzuela@arauco.cl"},
            {'pregunta': "Organización / Empresa", 'respuesta': "Celulosa Arauco Planta Los Ángeles"},
            {'pregunta': "¿Qué servicio requiere?", 'respuesta': "Gestión de Personas y Reclutamiento Activo"},
            {'pregunta': "¿Cuál es la urgencia de la consultoría?", 'respuesta': "Alta (Reclutamiento crítico de operarios de caldera en 15 días)"},
            {'pregunta': "¿Tiene acreditación vigente con alguna norma?", 'respuesta': "Acreditación Corma vigente"},
            {'pregunta': "Comentarios adicionales", 'respuesta': "Necesitamos evaluar una terna para supervisor de patio de maderas. A la brevedad."}
        ]
    },
    {
        'id': 2,
        'timestamp': "14/08/2026 17:41:05",
        'email': "m.carrasco@cmpc.cl",
        'nombre': "María Paula Carrasco",
        'rut': "18.304.591-K",
        'detalle': [
            {'pregunta': "Marca temporal", 'respuesta': "14/08/2026 17:41:05"},
            {'pregunta': "Nombre Completo", 'respuesta': "María Paula Carrasco"},
            {'pregunta': "RUT", 'respuesta': "18.304.591-K"},
            {'pregunta': "Correo Electrónico Corporativo", 'respuesta': "m.carrasco@cmpc.cl"},
            {'pregunta': "Organización / Empresa", 'respuesta': "CMPC Maderas S.A."},
            {'pregunta': "¿Qué servicio requiere?", 'respuesta': "Capacitación y Formación Laboral (OTEC)"},
            {'pregunta': "¿Número estimado de participantes?", 'respuesta': "45 operarios en 3 turnos"},
            {'pregunta': "¿Qué temáticas prioritarias requiere abordar?", 'respuesta': "Trabajo en equipo, resiliencia post-incendios y comunicación asertiva"},
            {'pregunta': "Comentarios adicionales", 'respuesta': "Deseamos imputar el gasto mediante franquicia tributaria SENCE."}
        ]
    },
    {
        'id': 3,
        'timestamp': "14/08/2026 19:15:44",
        'email': "contacto@agroforestal.cl",
        'nombre': "Roberto Muñoz Letelier",
        'rut': "9.314.502-8",
        'detalle': [
            {'pregunta': "Marca temporal", 'respuesta': "14/08/2026 19:15:44"},
            {'pregunta': "Nombre Completo", 'respuesta': "Roberto Muñoz Letelier"},
            {'pregunta': "RUT", 'respuesta': "9.314.502-8"},
            {'pregunta': "Correo Electrónico Corporativo", 'respuesta': "contacto@agroforestal.cl"},
            {'pregunta': "Organización / Empresa", 'respuesta': "Sociedad Agroforestal Biobío Ltda."},
            {'pregunta': "¿Qué servicio requiere?", 'respuesta': "Salud Ocupacional y Diagnósticos de Clima"},
            {'pregunta': "¿Ha aplicado el protocolo ISTAS-21 / CEAL-SM?", 'respuesta': "No, requerimos asesoría completa desde cero para cumplimiento legal"},
            {'pregunta': "Comentarios adicionales", 'respuesta': "Tenemos una fiscalización pendiente y necesitamos levantar el comité paritario y protocolo psicosocial."}
        ]
    }
]

@never_cache
@login_required(login_url='login')
def dashboard_view(request):
    if not request.user.is_superuser:
        # Portal del Candidato / Usuario regular
        cursos_activos = [
            {
                'id': '1',
                'codigo': 'GP-01',
                'titulo': "Gestión Estratégica y Liderazgo en el Sector Forestal",
                'categoria': "Gestión de Personas",
                'progreso': 75,
                'fecha_inicio': "10/08/2026",
                'estado': "En Curso"
            }
        ]
        
        cursos_completados = [
            {
                'id': '2',
                'codigo': 'SO-02',
                'titulo': "Seguridad Industrial y Prevención de Riesgos Acreditados",
                'categoria': "Salud Ocupacional",
                'progreso': 100,
                'fecha_inicio': "01/06/2026",
                'fecha_fin': "15/07/2026",
                'estado': "Completado"
            }
        ]
        
        evaluaciones = [
            {
                'nombre': "Evaluación Psicolaboral General",
                'fecha': "14/08/2026",
                'resultado': "Aprobado (Apto)",
                'comentarios': "Cumple satisfactoriamente con el perfil requerido para cargos industriales.",
                'estado': 'aprobado'
            },
            {
                'nombre': "Acreditación Vial Especializada Corma",
                'fecha': "16/08/2026",
                'resultado': "Pendiente de Aprobación",
                'comentarios': "Evaluación en proceso de revisión por parte de los consultores.",
                'estado': 'pendiente'
            }
        ]
        
        certificados = [
            {
                'id': '2',
                'curso_titulo': "Seguridad Industrial y Prevención de Riesgos Acreditados",
                'fecha_emision': "15/07/2026",
                'codigo_verificacion': "CERT-SO-2026-9042"
            }
        ]
        
        compras = [
            {
                'factura': "FA-2026-0891",
                'fecha': "12/08/2026",
                'servicio': "Curso - Gestión Estratégica y Liderazgo Forestal",
                'monto': "$125.000 CLP",
                'estado_pago': "Pagado",
                'medio_pago': "Transbank Webpay"
            },
            {
                'factura': "FA-2026-0412",
                'fecha': "05/06/2026",
                'servicio': "Curso - Seguridad Industrial y Prevención de Riesgos",
                'monto': "$85.000 CLP",
                'estado_pago': "Pagado",
                'medio_pago': "Transbank Webpay"
            }
        ]
        
        user_contexto = {
            'activo': 'dashboard',
            'cursos_activos': cursos_activos,
            'cursos_completados': cursos_completados,
            'evaluaciones': evaluaciones,
            'certificados': certificados,
            'compras': compras
        }
        return render(request, 'core/user_portal.html', user_contexto)

    # Portal de Administración (Superusuario)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'save_google_sheet':
            url = request.POST.get('google_sheet_url', '').strip()
            setting, created = SystemSetting.objects.get_or_create(key='google_sheet_url')
            setting.value = url
            setting.save()
            messages.success(request, "Configuración del Google Sheet de encuesta actualizada con éxito.")
            return redirect('dashboard')

    seed_default_carousel_if_empty()
    solicitudes = Solicitud.objects.all().order_by('-fecha')
    servicios = Servicio.objects.all().order_by('codigo')
    carousel_images = CarouselImage.objects.all().order_by('orden')
    
    # Contadores
    total_solicitudes = solicitudes.count()
    total_servicios = servicios.count()
    total_clientes = solicitudes.values('rut').distinct().count()
    
    google_sheet_url_setting = SystemSetting.objects.filter(key='google_sheet_url').first()
    google_sheet_url = google_sheet_url_setting.value if google_sheet_url_setting else ''
    
    survey_responses = []
    survey_error = None
    using_mock = False
    
    if google_sheet_url:
        headers, survey_responses, survey_error = fetch_and_parse_google_sheet(google_sheet_url)
    else:
        survey_responses = MOCK_SURVEY_RESPONSES
        using_mock = True
        
    contexto = {
        "activo": "dashboard",
        "solicitudes": solicitudes,
        "servicios": servicios,
        "carousel_images": carousel_images,
        "total_solicitudes": total_solicitudes,
        "total_servicios": total_servicios,
        "total_clientes": total_clientes,
        "google_sheet_url": google_sheet_url,
        "survey_responses": survey_responses,
        "survey_error": survey_error,
        "using_mock": using_mock
    }
    return render(request, 'core/dashboard.html', contexto)


@login_required(login_url='login')
def descargar_certificado_pdf(request, cert_id):
    from io import BytesIO
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from django.http import HttpResponse
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    # Borde exterior verde
    p.setStrokeColor(colors.HexColor('#3C612E'))
    p.setLineWidth(5)
    p.rect(20, 20, width - 40, height - 40)
    
    # Borde interior dorado
    p.setStrokeColor(colors.HexColor('#C09A46'))
    p.setLineWidth(2)
    p.rect(26, 26, width - 52, height - 52)
    
    # Contenidos
    p.setFont("Helvetica-Bold", 30)
    p.setFillColor(colors.HexColor('#1F3318'))
    p.drawCentredString(width / 2.0, height - 110, "DIPLOMA DE CAPACITACIÓN")
    
    p.setFont("Helvetica", 14)
    p.setFillColor(colors.HexColor('#5D7653'))
    p.drawCentredString(width / 2.0, height - 145, "OTORGADO POR PROTEA CONSULTORÍA")
    
    p.setFont("Helvetica-Oblique", 15)
    p.setFillColor(colors.HexColor('#1F3318'))
    p.drawCentredString(width / 2.0, height - 200, "Se certifica formalmente que")
    
    nombre_alumno = f"{request.user.first_name} {request.user.last_name}".strip().upper()
    if not nombre_alumno or nombre_alumno == 'USUARIO' or request.user.username == 'usuario':
        nombre_alumno = "JUAN CARLOS PÉREZ VALENZUELA"
        
    p.setFont("Helvetica-Bold", 26)
    p.setFillColor(colors.HexColor('#C20E3A'))
    p.drawCentredString(width / 2.0, height - 245, nombre_alumno)
    
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.HexColor('#5D7653'))
    p.drawCentredString(width / 2.0, height - 275, "RUT: 15.482.912-3")
    
    curso_nombre = "Gestión de Personas y Reclutamiento Activo"
    if str(cert_id) == '2':
        curso_nombre = "Seguridad Industrial y Prevención de Riesgos Acreditados"
        
    p.setFont("Helvetica", 13)
    p.setFillColor(colors.HexColor('#1F3318'))
    p.drawCentredString(width / 2.0, height - 315, "Ha aprobado satisfactoriamente el curso teórico-práctico de:")
    
    p.setFont("Helvetica-Bold", 17)
    p.setFillColor(colors.HexColor('#3C612E'))
    p.drawCentredString(width / 2.0, height - 345, f"\"{curso_nombre}\"")
    
    p.setFont("Helvetica-Oblique", 11)
    p.setFillColor(colors.HexColor('#5D7653'))
    p.drawCentredString(width / 2.0, height - 380, "Duración: 40 horas cronológicas | Calificación: 6.8 (Escala 1.0 a 7.0)")
    
    p.setFont("Helvetica", 11)
    p.setFillColor(colors.HexColor('#1F3318'))
    p.drawCentredString(width / 2.0, height - 420, "Emitido en Los Ángeles, Chile, el 18 de Agosto de 2026.")
    
    # Firmas
    p.setStrokeColor(colors.HexColor('#5D7653'))
    p.setLineWidth(1)
    
    p.line(120, 100, 300, 100)
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor('#1F3318'))
    p.drawCentredString(210, 85, "Patricia Toro Valenzuela")
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.HexColor('#5D7653'))
    p.drawCentredString(210, 72, "Directora Ejecutiva Protea")
    
    p.line(width - 300, 100, width - 120, 100)
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor('#1F3318'))
    p.drawCentredString(width - 210, 85, "Representante Legal OTEC")
    p.setFont("Helvetica", 8)
    p.setFillColor(colors.HexColor('#5D7653'))
    p.drawCentredString(width - 210, 72, "Acreditación Corma SENCE")
    
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificado_{cert_id}.pdf"'
    return response


@never_cache
@login_required(login_url='login')
def admin_carousel_crear(request):
    if CarouselImage.objects.count() >= 5:
        messages.error(request, "No se pueden agregar más de 5 imágenes al carrusel para evitar la saturación visual del sitio.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        orden = request.POST.get('orden', 0)
        imagen_archivo = request.FILES.get('imagen_archivo')
        
        if not imagen_archivo:
            messages.error(request, "Debe seleccionar un archivo de imagen.")
            return redirect('dashboard')
            
        # Guardar archivo dinámicamente en static/img/
        filename = f"carousel_{int(time.time())}_{imagen_archivo.name.replace(' ', '_')}"
        filepath = os.path.join(settings.BASE_DIR, 'static', 'img', filename)
        
        try:
            with open(filepath, 'wb+') as destination:
                for chunk in imagen_archivo.chunks():
                    destination.write(chunk)
        except Exception as e:
            messages.error(request, f"Error al guardar la imagen: {e}")
            return redirect('dashboard')
            
        imagen_path = f"img/{filename}"
        subtitulo = request.POST.get('subtitulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        CarouselImage.objects.create(
            imagen_path=imagen_path,
            subtitulo=subtitulo,
            titulo=titulo,
            descripcion=descripcion,
            orden=orden
        )
        messages.success(request, "Imagen agregada al carrusel correctamente.")
        return redirect('dashboard')
        
    return render(request, 'core/admin_carousel_form.html', {'action': 'crear'})


@never_cache
@login_required(login_url='login')
def admin_carousel_editar(request, id):
    slide = get_object_or_404(CarouselImage, id=id)
    if request.method == 'POST':
        slide.titulo = request.POST.get('titulo')
        slide.orden = request.POST.get('orden', 0)
        imagen_archivo = request.FILES.get('imagen_archivo')
        
        if imagen_archivo:
            # Guardar nuevo archivo
            filename = f"carousel_{int(time.time())}_{imagen_archivo.name.replace(' ', '_')}"
            filepath = os.path.join(settings.BASE_DIR, 'static', 'img', filename)
            try:
                with open(filepath, 'wb+') as destination:
                    for chunk in imagen_archivo.chunks():
                        destination.write(chunk)
                slide.imagen_path = f"img/{filename}"
            except Exception as e:
                messages.error(request, f"Error al guardar la nueva imagen: {e}")
                return redirect('dashboard')
                
        slide.subtitulo = request.POST.get('subtitulo', '').strip()
        slide.descripcion = request.POST.get('descripcion', '').strip()
        slide.save()
        messages.success(request, "Imagen del carrusel editada correctamente.")
        return redirect('dashboard')
        
    return render(request, 'core/admin_carousel_form.html', {'action': 'editar', 'slide': slide})


@never_cache
@login_required(login_url='login')
def admin_carousel_eliminar(request, id):
    slide = get_object_or_404(CarouselImage, id=id)
    slide.delete()
    messages.success(request, "Imagen eliminada del carrusel.")
    return redirect('dashboard')


@never_cache
@login_required(login_url='login')
def admin_servicio_crear(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        categoria = request.POST.get('categoria')
        titulo = request.POST.get('titulo')
        resumen = request.POST.get('resumen')
        detalle = request.POST.get('detalle')
        duracion = request.POST.get('duracion')
        modalidad = request.POST.get('modalidad')
        
        # Procesar entregables (separados por salto de línea)
        entregables_text = request.POST.get('entregables', '')
        entregables = [line.strip() for line in entregables_text.split('\n') if line.strip()]
        
        if Servicio.objects.filter(codigo=codigo).exists():
            messages.error(request, f"Ya existe un servicio con el código '{codigo}'.")
            return render(request, 'core/admin_servicio_form.html', {
                'action': 'crear',
                'servicio_data': request.POST
            })
            
        Servicio.objects.create(
            codigo=codigo,
            categoria=categoria,
            titulo=titulo,
            resumen=resumen,
            detalle=detalle,
            duracion=duracion,
            modalidad=modalidad,
            entregables=entregables
        )
        messages.success(request, "Servicio creado correctamente.")
        return redirect('dashboard')
        
    return render(request, 'core/admin_servicio_form.html', {'action': 'crear'})


@never_cache
@login_required(login_url='login')
def admin_servicio_editar(request, codigo):
    servicio = get_object_or_404(Servicio, codigo=codigo)
    if request.method == 'POST':
        servicio.categoria = request.POST.get('categoria')
        servicio.titulo = request.POST.get('titulo')
        servicio.resumen = request.POST.get('resumen')
        servicio.detalle = request.POST.get('detalle')
        servicio.duracion = request.POST.get('duracion')
        servicio.modalidad = request.POST.get('modalidad')
        
        # Procesar entregables
        entregables_text = request.POST.get('entregables', '')
        servicio.entregables = [line.strip() for line in entregables_text.split('\n') if line.strip()]
        
        servicio.save()
        messages.success(request, "Servicio actualizado correctamente.")
        return redirect('dashboard')
        
    # Convertir entregables de lista a formato texto con saltos de línea para el textarea
    entregables_str = "\n".join(servicio.entregables)
    return render(request, 'core/admin_servicio_form.html', {
        'action': 'editar',
        'servicio': servicio,
        'entregables_str': entregables_str
    })


@never_cache
@login_required(login_url='login')
def admin_servicio_eliminar(request, codigo):
    servicio = get_object_or_404(Servicio, codigo=codigo)
    servicio.delete()
    messages.success(request, "Servicio eliminado correctamente.")
    return redirect('dashboard')


@never_cache
@login_required(login_url='login')
def admin_solicitud_editar(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)
    if request.method == 'POST':
        solicitud.estado = request.POST.get('estado')
        solicitud.nombre = request.POST.get('nombre')
        solicitud.rut = request.POST.get('rut')
        solicitud.email = request.POST.get('email')
        solicitud.telefono = request.POST.get('telefono')
        solicitud.organizacion = request.POST.get('organizacion')
        solicitud.mensaje = request.POST.get('mensaje')
        
        solicitud.save()
        messages.success(request, "Solicitud actualizada correctamente.")
        return redirect('dashboard')
        
    return render(request, 'core/admin_solicitud_form.html', {'solicitud': solicitud})


@never_cache
@login_required(login_url='login')
def admin_solicitud_eliminar(request, id):
    solicitud = get_object_or_404(Solicitud, id=id)
    solicitud.delete()
    messages.success(request, "Solicitud eliminada correctamente.")
    return redirect('dashboard')


def solicitud_exito(request):
    ticket_id = request.GET.get('ticket')
    sol = get_object_or_404(Solicitud, ticket=ticket_id)
    contexto = {
        "solicitud": sol,
        "activo": "servicios"
    }
    return render(request, "core/solicitud_exito.html", contexto)
