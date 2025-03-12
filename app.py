from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def extract_data(xpath, driver):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.text
    except:
        return ""

def scrape_maps(search_for, lat, lng, zoom, lang, total=20):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    url = f"https://www.google.com/maps/search/{search_for}/@{lat},{lng},{zoom}z?&hl={lang}"
    driver.get(url)
    
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Accept all"]'))
        )
        accept_button.click()
    except:
        pass

    results = []
    previously_counted = 0
    while True:
        driver.execute_script("window.scrollBy(0, 10000);")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "https://www.google.com/maps/place")]'))
        )

        current_count = len(driver.find_elements(By.XPATH, '//a[contains(@href, "https://www.google.com/maps/place")]'))
        if current_count >= total:
            listings = driver.find_elements(By.XPATH, '//a[contains(@href, "https://www.google.com/maps/place")]')[:total]
            break
        elif current_count == previously_counted:
            listings = driver.find_elements(By.XPATH, '//a[contains(@href, "https://www.google.com/maps/place")]')
            break
        else:
            previously_counted = current_count

    for listing in listings:
        listing.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]'))
        )
        
        try:
            share_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[4]/div[5]/button/span'))
            )
            share_button.click()
            short_url_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@class="vrsrZe"]'))
            )
            short_url = short_url_input.get_attribute("value")
            
            image_url = driver.execute_script('''
                return document.querySelector('img.Jn12ke') ? document.querySelector('img.Jn12ke').src : "";
            ''')
            
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="modal-dialog"]/div/div[2]/div/button/span'))
            )
            close_button.click()
        except:
            short_url = ""
            image_url = ""
        
        data = {
            "nombre": extract_data('//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]', driver),
            "imagen": image_url,
            "direccion": extract_data('//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]', driver),
            "Web": extract_data('//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]', driver),
            "GMB": short_url, 
            "Phone_Number": extract_data('//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]', driver),
            "Reviews_Count": extract_data('//div[@class="TIHn2 "]//div[@class="fontBodyMedium dmRWX"]//div//span//span//span[@aria-label]', driver),
            "Reviews_Average": extract_data('//div[@class="TIHn2 "]//div[@class="fontBodyMedium dmRWX"]//div//span[@aria-hidden]', driver),
            "Responde_reviews": bool(extract_data('//*[@class="nM6d2c"]', driver)),
            "Store_Shopping": extract_data('//div[@class="LTs0Rc"][1]', driver),
            "In_Store_Pickup": extract_data('//div[@class="LTs0Rc"][2]', driver),
            "Store_Delivery": extract_data('//div[@class="LTs0Rc"][3]', driver),
            "tipologia": extract_data('//div[@class="LBgpqf"]//button[@class="DkEaL "]', driver),
            "descripcion": extract_data('//div[@class="WeS02d fontBodyMedium"]//div[@class="PYvSYb "]', driver),
        }
        results.append(data)
    
    driver.quit()
    return results

@app.route('/get_places', methods=['GET'])
def get_places():
    search_for = request.args.get('Busqueda', 'pizza')
    lat = request.args.get('Latitud', '29.1978347')
    lng = request.args.get('Longitud', '69.762367')
    zoom = request.args.get('Zoom', '9')
    lang = request.args.get('idioma', 'es')
    total = int(request.args.get('total', 20))

    results = scrape_maps(search_for, lat, lng, zoom, lang, total)
    return jsonify(results)

@app.route('/', methods=['GET'])
def holamundo():
    return "Hola Mundo"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)

