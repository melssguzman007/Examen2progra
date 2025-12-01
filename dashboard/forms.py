from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Alumno

class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'required': True}) 
    )
    
    class Meta:
        model = User
        # 🟢 CORRECCIÓN: Usar los campos por defecto más el email 🟢
        fields = ("username", "email", "password2") # Agregamos password2 (password1 y password2 son automáticos)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aquí eliminamos los campos password del loop de estilización para no duplicar el error
        fields_to_style = ['username', 'email', 'password2'] # 🟢 CORREGIR 🟢
        
        for field_name in fields_to_style:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['class'] = 'form-control'
            
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"] # Asignamos el email
        if commit:
            user.save()
        return user

# dashboard/forms.py

# ... (Clase RegistroForm, que ya parece estar bien) ...

# Formulario para crear/editar Alumno
class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        # 🟢 CORRECCIÓN: Usar la nomenclatura de Python (minúsculas sin acentos) 🟢
        fields = ['dni', 'nombre_completo', 'legajo', 'carrera', 'telefono', 'nota_final']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicamos la clase form-control a todos los campos de AlumnoForm
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'