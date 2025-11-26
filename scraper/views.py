from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from bs4 import BeautifulSoup
import requests
import urllib.parse
from django.conf import settings


@login_required
def scraper_view(request):
    resultados = None
    keyword = None
    mensaje = None 
    
   
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    
    if request.method == 'POST':
        keyword = request.POST.get('keyword', '').strip()
        
        if keyword:
           
            base_url = "https://es.wikipedia.org/wiki/Especial:Buscar?search="
            search_url = base_url + urllib.parse.quote_plus(keyword) 

            try:
                
                response = requests.get(search_url, headers=HEADERS, timeout=10) 
                response.raise_for_status() 
                
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
               
                result_elements = soup.select('ul.mw-search-results li a') 
                
                resultados = []
                for element in result_elements[:5]: 
                    title = element.get('title')
                    
                    url = "https://es.wikipedia.org" + element.get('href') if element.get('href') and element.get('href').startswith('/') else element.get('href')
                    if title and url:
                        resultados.append({'titulo': title, 'url': url})

                
                if resultados:
                    email_body = f"Resultados de scraping para la palabra clave '{keyword}':\n\n"
                    for i, res in enumerate(resultados):
                        email_body += f"{i+1}. {res['titulo']}\n   URL: {res['url']}\n"
                    
                    send_mail(
                        f'Resultados de Scraping para "{keyword}"',
                        email_body,
                        settings.DEFAULT_FROM_EMAIL,
                        [request.user.email], # Enviar al usuario
                        fail_silently=False,
                    )
                    mensaje = f"Scraping completado. Se han encontrado {len(resultados)} resultados y se enviaron por correo a {request.user.email}."
                else:
                    mensaje = f"Scraping completado, pero no se encontraron resultados para '{keyword}'."
                
            except requests.exceptions.HTTPError as e:
               
                mensaje = f"Error HTTP al realizar la solicitud de scraping: {e}"
                
            except requests.exceptions.RequestException as e:
                
                mensaje = f"Error de Conexión al realizar el scraping: {e}"

            except Exception as e:
                mensaje = f"Ocurrió un error inesperado durante el scraping: {e}"
        else:
            mensaje = "Por favor, ingrese una palabra clave para iniciar el scraping."


    context = {
        'keyword': keyword,
        'resultados': resultados,
        'mensaje': mensaje,
    }
    
    return render(request, 'scraper/scraper.html', context)