from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

@login_required
def scraper_view(request):
    resultados = []
    palabra_clave = ""
    
    if request.method == 'POST':
        palabra_clave = request.POST.get('palabra_clave', '').strip()
        enviar_email = request.POST.get('enviar_email') == 'on'
        
        if palabra_clave:
            try:
                # Scraping de Wikipedia (educativo y genérico)
                url = f"https://es.wikipedia.org/w/api.php?action=opensearch&search={quote_plus(palabra_clave)}&limit=10&format=json"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # El formato de respuesta de opensearch es:
                    # [query, [titles], [descriptions], [urls]]
                    if len(data) >= 4:
                        titulos = data[1]
                        descripciones = data[2]
                        urls = data[3]
                        
                        for i in range(len(titulos)):
                            resultados.append({
                                'titulo': titulos[i],
                                'descripcion': descripciones[i] if i < len(descripciones) else 'Sin descripción',
                                'url': urls[i] if i < len(urls) else '#'
                            })
                    
                    if not resultados:
                        messages.warning(request, f'No se encontraron resultados para "{palabra_clave}"')
                    else:
                        messages.success(request, f'Se encontraron {len(resultados)} resultados')
                        
                        # Enviar por correo si se solicitó
                        if enviar_email:
                            try:
                                contenido_email = f"Resultados de búsqueda para: {palabra_clave}\n\n"
                                for idx, res in enumerate(resultados, 1):
                                    contenido_email += f"{idx}. {res['titulo']}\n"
                                    contenido_email += f"   {res['descripcion']}\n"
                                    contenido_email += f"   {res['url']}\n\n"
                                
                                send_mail(
                                    subject=f'Resultados de Búsqueda: {palabra_clave}',
                                    message=contenido_email,
                                    from_email=settings.DEFAULT_FROM_EMAIL,
                                    recipient_list=[request.user.email],
                                    fail_silently=False,
                                )
                                messages.success(request, 'Resultados enviados por correo exitosamente')
                            except Exception as e:
                                messages.error(request, f'Error al enviar correo: {str(e)}')
                
                else:
                    messages.error(request, f'Error al realizar la búsqueda. Código: {response.status_code}')
                    
            except requests.RequestException as e:
                messages.error(request, f'Error de conexión: {str(e)}')
            except Exception as e:
                messages.error(request, f'Error inesperado: {str(e)}')
        else:
            messages.warning(request, 'Por favor ingresa una palabra clave')
    
    context = {
        'resultados': resultados,
        'palabra_clave': palabra_clave
    }
    
    return render(request, 'scraper/scraper.html', context)