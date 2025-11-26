import os
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



def registro_view(request):
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
                    fail_silently=False,
                )
            except Exception as e:
               
                print(f"Error al enviar correo de bienvenida: {e}")
                
            login(request, user) 
            return redirect('dashboard:dashboard')
    else:
        form = RegistroForm()
    
    return render(request, 'dashboard/registro.html', {'form': form})



@login_required
def dashboard_view(request):
   
    alumnos = Alumno.objects.filter(usuario=request.user).order_by('nombre_completo')
    
    form = AlumnoForm()
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            try:
                nuevo_alumno = form.save(commit=False)
                nuevo_alumno.usuario = request.user
                nuevo_alumno.save()
                return redirect('dashboard:dashboard')
            except Exception as e:
                
                return render(request, 'dashboard/dashboard.html', {
                    'alumnos': alumnos,
                    'form': form,
                    'mensaje_error': f'Error al guardar el alumno: {e}'
                })

    return render(request, 'dashboard/dashboard.html', {
        'alumnos': alumnos,
        'form': form
    })




@login_required
def generar_y_enviar_pdf(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id, usuario=request.user)
    temp_filename = f"temp_{alumno.legajo}.pdf"
    
   
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

    try:
       
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
        
      
        dashboard_url = reverse('dashboard:dashboard')
        
       
        return redirect(f"{dashboard_url}?success_message=PDF enviado correctamente para {alumno.nombre_completo} a {email_docente} y {request.user.email}.")

    except Exception as e:
        
        print(f"Error al enviar el email con PDF: {e}")
        
       
        dashboard_url = reverse('dashboard:dashboard')

       
        return redirect(f"{dashboard_url}?error_message=Error al enviar el PDF: {e}")
        
    finally:
       
        if os.path.exists(temp_filename):
            os.remove(temp_filename)