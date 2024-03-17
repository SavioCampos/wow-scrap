from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm
import datetime
import requests
import re


class Item:
    def __init__(self, server, precio, cantidad):
        self.server = server
        self.precio = precio
        self.cantidad = cantidad

#Configuracion de bot de Telegram
TOKEN = '7070477668:AAFnG0aHBZjDA0xyRhf9VZoQWmKUnK49jP0'
chat_id = '-1002124524842'

def enviar_mensaje(mensaje):
    requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data={'chat_id': chat_id, 'text': mensaje, 'parse_mode': 'HTML'})

# Parametros
URLS = ["https://undermine.exchange/#us-goldrinn/208426-444",
       "https://undermine.exchange/#us-goldrinn/208420-457"]
UMBRAL = [30000, 120000]

# Configura el driver de Selenium
options = Options()
options.add_argument('--headless')  # Ejecuta Chrome en modo headless


# Inicializa el navegador Chrome con las opciones configuradas
for index, URL in enumerate(URLS):
    # Abre la página web
    driver = webdriver.Chrome(options=options)
    driver.get(URL)

    # Espera a que el JavaScript se cargue 
    try:
        # Define una espera explícita con un tiempo máximo de espera de 10 segundos o hasta que encuentre un elemento especifico
        elemento = WebDriverWait(driver, 360).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="list"]//table//tbody//*'))
        )
        # Obtiene el HTML después de que el JavaScript se haya ejecutado
        html = driver.page_source

        # Cierra el navegador
        driver.quit()

        # Analiza el HTML con BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        div = soup.find('div', {'class': 'list'})
        title = soup.find('span', {'class': 'title q4'})
        name = title.find_next('a').get_text()
        table = div.find_next('table')
        items = []


        for row in tqdm(table.findAll('tr')[1:]):
            realm = row.findAll('td')[0]['data-sort-value']
            price = int(row.findAll('td')[1]['data-sort-value'])
            quantity = int(row.findAll('td')[2]['data-sort-value'])
            item = Item(realm, int(price/10000), quantity)
            items.append(item)

        items_con_stock = filter(lambda obj: obj.cantidad > 0, items)
        item_menor_precio = min(items_con_stock, key=lambda obj: obj.precio)
        tiempo = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        server_url = item_menor_precio.server.lower().replace(" ", "-")
        new_URL = re.sub(r'(?<=us-)[^/]+', server_url, URL)
        mensaje = f"{tiempo}: - Item: {name}, Server: {item_menor_precio.server}, Precio: {item_menor_precio.precio}, Cantidad: {item_menor_precio.cantidad}, URL: {new_URL}"
        print(mensaje)
        if item_menor_precio.precio <= UMBRAL[index]:
            enviar_mensaje(mensaje)

    except Exception as e:
        print("Se agotó el tiempo de espera o el elemento no se encontró:", e)



