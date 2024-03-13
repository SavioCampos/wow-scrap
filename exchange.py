from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Item:
    def __init__(self, server, precio, cantidad):
        self.server = server
        self.precio = precio
        self.cantidad = cantidad

# Parametros
URL = "https://undermine.exchange/#us-goldrinn/208426-444"
UMBRAL = 30000
EMAIL = 'sak.kancer@gmail.com'

# Configuración del servidor SMTP y credenciales para Gmail
smtp_server = 'smtp.gmail.com'
smtp_port = 587  # Puerto SMTP para Gmail

# Direcciones de correo electrónico
sender_email = 'scrapwowexchange@gmail.com'
receiver_email = EMAIL

# Credenciales de Gmail
smtp_username = 'scrapwowexchange@gmail.com'
smtp_password = 'ixru crmq wmwx inrg'

# Configura el driver de Selenium
options = Options()
options.add_argument('--headless')  # Ejecuta Chrome en modo headless


# Inicializa el navegador Chrome con las opciones configuradas
driver = webdriver.Chrome(options=options)

# Abre la página web
driver.get(URL)

# Espera a que el JavaScript se cargue 
try:
    # Define una espera explícita con un tiempo máximo de espera de 10 segundos o hasta que encuentre un elemento especifico
    elemento = WebDriverWait(driver, 180).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="list"]//table//tbody//*'))
    )

    
except Exception as e:
    print("Se agotó el tiempo de espera o el elemento no se encontró:", e)


# Obtiene el HTML después de que el JavaScript se haya ejecutado
html = driver.page_source

# Cierra el navegador
driver.quit()

# Analiza el HTML con BeautifulSoup
soup = BeautifulSoup(html, "lxml")
div = soup.find('div', {'class': 'list'})
table = div.find_next('table')
print(table)
items = []

for row in tqdm(table.findAll('tr')[1:]):
    realm = row.findAll('td')[0]['data-sort-value']
    price = int(row.findAll('td')[1]['data-sort-value'])
    quantity = int(row.findAll('td')[2]['data-sort-value'])
    item = Item(realm, int(price/10000), quantity)
    items.append(item)

items_con_stock = filter(lambda obj: obj.cantidad > 0, items)
item_menor_precio = min(items_con_stock, key=lambda obj: obj.precio)

print(f"Server: {item_menor_precio.server}, Precio: {item_menor_precio.precio}, Cantidad: {item_menor_precio.cantidad}")
if item_menor_precio.precio <= UMBRAL:
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'Se ha detectado una oferta en un item'

    # Cuerpo del mensaje
    body = f"Server: {item_menor_precio.server}, Precio: {item_menor_precio.precio}, Cantidad: {item_menor_precio.cantidad}"
    message.attach(MIMEText(body, 'plain'))

    # Iniciar conexión con el servidor SMTP de Gmail
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Iniciar cifrado TLS

    # Iniciar sesión en el servidor SMTP de Gmail
    server.login(smtp_username, smtp_password)

    # Enviar correo electrónico
    text = message.as_string()
    server.sendmail(sender_email, receiver_email, text)

    # Cerrar conexión con el servidor SMTP de Gmail
    server.quit()

