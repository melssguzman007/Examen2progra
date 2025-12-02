import os
import io 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse 
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from .forms import RegistroForm, AlumnoForm
from .models import Alumno

# --- 1. VISTA DE REGISTRO ---
def registro_view(request):
    """Maneja el registro de nuevos usuarios y el envío de correo de bienvenida."""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            try:
                send_mail(
                    '¡Bienvenido a nuestro sistema!',
                    f'Hola {user.username},\n\nGracias por registrarte en el sistema del examen parcial.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error al enviar correo de bienvenida: {e}")
                
            login(request, user) 
            return redirect('dashboard:dashboard')
    else:
        form = RegistroForm()
    
    return render(request, 'dashboard/registro.html', {'form': form})


# --- 2. VISTA DE DASHBOARD (Creación y Listado) ---
@login_required
def dashboard_view(request):
    """Muestra la lista de alumnos del usuario y maneja la creación de nuevos alumnos."""
    
    # 🟢 FIX CLAVE: Inicializa las variables antes del if 🟢
    alumnos = Alumno.objects.filter(usuario=request.user)
    form = AlumnoForm()
    
    if request.method == 'POST':
        # Maneja la creación de un nuevo alumno
        form = AlumnoForm(request.POST)
        if form.is_valid():
            nuevo_alumno = form.save(commit=False)
            nuevo_alumno.usuario = request.user # Asigna el alumno al usuario actual
            nuevo_alumno.save()
            return redirect('dashboard:dashboard') # Redirige al dashboard (GET)
    
    # Maneja mensajes de éxito/error de redirecciones anteriores (ej: edición/eliminación/pdf)
    success_message = request.GET.get('success_message')
    error_message = request.GET.get('error_message')

    context = {
        'alumnos': alumnos,
        'form': form,
        'mensaje_exito': success_message,
        'mensaje_error': error_message,
    }
    return render(request, 'dashboard/dashboard.html', context)


# --- 3. VISTA DE EDICIÓN ---
@login_required
def alumno_editar(request, pk):
    """Permite editar un registro de alumno existente."""
    # Asegura que solo el dueño pueda editar (usamos 'usuario=request.user' como en el model)
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        # Instancia el formulario con los datos POST Y la instancia del alumno a modificar
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            # 🟢 FIX: Redirige con mensaje de éxito como parámetro GET 🟢
            dashboard_url = reverse('dashboard:dashboard')
            return redirect(f"{dashboard_url}?success_message=Alumno actualizado correctamente.")
    else:
        # Si es un GET, instancia el formulario con la data actual del alumno
        form = AlumnoForm(instance=alumno)
        
    context = {
        'form': form,
        'alumno': alumno # Necesario para el título y la URL en el template
    }
    return render(request, 'dashboard/alumno_form.html', context)


# --- 4. VISTA DE ELIMINACIÓN ---
@login_required
def alumno_eliminar(request, pk):
    """Elimina un registro de alumno."""
    # Asegura que solo el dueño pueda eliminar
    alumno = get_object_or_404(Alumno, pk=pk, usuario=request.user)
    alumno.delete()
    # 🟢 FIX: Redirige con mensaje de éxito como parámetro GET 🟢
    dashboard_url = reverse('dashboard:dashboard')
    return redirect(f"{dashboard_url}?success_message=Alumno eliminado correctamente.")


# --- 5. VISTA DE GENERACIÓN Y ENVÍO DE PDF ---
@login_required
def generar_y_enviar_pdf(request, alumno_id):
    """Genera un PDF del alumno, lo adjunta y lo envía por correo electrónico."""
    alumno = get_object_or_404(Alumno, id=alumno_id, usuario=request.user)
    temp_filename = f"temp_{alumno.legajo}_{alumno.id}.pdf"
    
    try:
        # --- 1. CREACIÓN DEL PDF EN EL DISCO ---
        p = canvas.Canvas(temp_filename, pagesize=A4)
        width, height = A4

        p.setFont('Helvetica-Bold', 18)
        p.drawString(50, height - 50, "Reporte de Alumno")
        p.setFont('Helvetica', 12)
        p.drawString(50, height - 90, f"Nombre: {alumno.nombre_completo}")
        p.drawString(50, height - 110, f"Legajo: {alumno.legajo}")
        p.drawString(50, height - 130, f"Carrera: {alumno.carrera}")
        p.setFillColor(colors.darkblue)
        p.rect(50, height - 180, 500, 20, fill=1)
        p.setFillColor(colors.white)
        p.drawString(55, height - 175, "DATOS ACADÉMICOS")
        p.setFillColor(colors.black)
        p.drawString(50, height - 210, f"Nota Final: {alumno.nota_final}")
        p.showPage()
        p.save()
        # --- FIN CREACIÓN ---

        # --- 2. LECTURA Y ENVÍO ---
        with open(temp_filename, "rb") as pdf_file:
            pdf_content = pdf_file.read()

        email_docente = "docente@tudominio.com" 
        
        email = EmailMessage(
            subject=f'Reporte de Alumno: {alumno.nombre_completo}',
            body=f'Adjunto se encuentra el reporte PDF del alumno {alumno.nombre_completo} (Legajo: {alumno.legajo}).\n\nEste reporte fue generado por el usuario {request.user.username}.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_docente, request.user.email], 
        )
        email.attach(f'reporte_{alumno.legajo}.pdf', pdf_content, 'application/pdf')
        email.send(fail_silently=False)
        
        # Redirección de éxito
        dashboard_url = reverse('dashboard:dashboard')
        return redirect(f"{dashboard_url}?success_message=PDF enviado correctamente para {alumno.nombre_completo} a {email_docente} y {request.user.email}.")

    except Exception as e:
        # Redirección de error
        print(f"Error durante la generación o envío del PDF: {e}")
        dashboard_url = reverse('dashboard:dashboard')
        return redirect(f"{dashboard_url}?error_message=Error al enviar el PDF: {e}")
        
    finally:
        # Asegura que el archivo temporal se borre
        if os.path.exists(temp_filename):
            os.remove(temp_filename)