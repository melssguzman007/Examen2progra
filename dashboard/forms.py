from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Alumno

# 1. Formulario de registro común
class RegistroForm(UserCreationForm):
    # Añadimos email al formulario de registro
    email = forms.EmailField(
        label="Correo Electrónico",
        # Aplicamos la clase form-control directamente al widget
        widget=forms.EmailInput(attrs={'class': 'form-control'}) 
    )
    
    class Meta:
        model = User
        fields = ("username", "email") # Campos a mostrar
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # FIX: Usamos 'password1' y 'password2' (los nombres correctos de UserCreationForm)
        # Aplicamos la clase form-control a los campos restantes
        fields_to_style = ['username', 'password1', 'password2'] 
        
        for field_name in fields_to_style:
            # Es importante verificar que el campo exista
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['class'] = 'form-control'
            
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"] # Asignamos el email
        if commit:
            user.save()
        return user

# Formulario para crear/editar Alumno
class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['nombre_completo', 'legajo', 'carrera', 'nota_final']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicamos la clase form-control a todos los campos de AlumnoForm
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'