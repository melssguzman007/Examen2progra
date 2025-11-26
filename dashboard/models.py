from django.db import models

# Create your models here.


from django.contrib.auth.models import User


class Alumno(models.Model):

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    

    nombre_completo = models.CharField(max_length=150)
    legajo = models.CharField(max_length=20, unique=True)
    carrera = models.CharField(max_length=100)
    
    
    nota_final = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.nombre_completo} ({self.legajo})"