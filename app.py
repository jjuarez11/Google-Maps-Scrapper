from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def extract_data(xpath, page):
    return page.locator(xpath).first.inner_text() if page.locator(xpath).count() > 0 else ""

def scrape_maps(search_for, lat, lng, zoom, lang, total=20):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu", "--disable-software-rasterizer"]
        )
        page = browser.new_page()
        
      
        url = f"https://www.google.com/maps/search/{search_for}/@{lat},{lng},{zoom}z?&hl={lang}"
        page.goto(url, timeout=60000)
        page.wait_for_timeout(1000)

        accept_button = page.locator('//button[@aria-label="Aceptar todo"]').first
        if accept_button.count() > 0:
            accept_button.click()
            page.wait_for_timeout(1000)

        previously_counted = 0
        while True:
            page.mouse.wheel(0, 10000)
            page.wait_for_selector('//a[contains(@href, "https://www.google.com/maps/place")]')

            if page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count() >= total:
                listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()[:total]
                listings = [listing.locator("xpath=..") for listing in listings]
                break
            elif page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count() == previously_counted:
                listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()
                break
            else:
                previously_counted = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count()

        results = []
        for listing in listings:
            listing.click()
            page.wait_for_selector('//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]')

            share_buttons = page.locator('//span[@class="DVeyrd "]')
            if share_buttons.count() >= 5:
                share_buttons.nth(4).click()
                page.wait_for_timeout(5000)
                short_url_input = page.locator('//input[@class="vrsrZe"]')
                short_url = short_url_input.input_value() if short_url_input.count() > 0 else ""
                
                image_url = page.evaluate('''
                    () => {
                        let img = document.querySelector('img.Jn12ke');
                        return img ? img.src : "";
                    }
                ''')

                close_button = page.locator('//span[@class="G6JA1c google-symbols"]').first
                if close_button.count() > 0:
                    close_button.click()
                    page.wait_for_timeout(500)
            else:
                short_url = ""
                image_url = ""
            
            data = {
                "nombre": extract_data('//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]', page),
                "imagen": image_url,
                "direccion": extract_data('//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]', page),
                "Web": extract_data('//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]', page),
                "GMB": short_url, 
                "Phone_Number": extract_data('//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]', page),
                "Reviews_Count": extract_data('//div[@class="TIHn2 "]//div[@class="fontBodyMedium dmRWX"]//div//span//span//span[@aria-label]', page),
                "Reviews_Average": extract_data('//div[@class="TIHn2 "]//div[@class="fontBodyMedium dmRWX"]//div//span[@aria-hidden]', page),
                "Responde_reviews": bool(extract_data('//*[@class="nM6d2c"]', page)),
                "Store_Shopping": extract_data('//div[@class="LTs0Rc"][1]', page),
                "In_Store_Pickup": extract_data('//div[@class="LTs0Rc"][2]', page),
                "Store_Delivery": extract_data('//div[@class="LTs0Rc"][3]', page),
                "tipologia": extract_data('//div[@class="LBgpqf"]//button[@class="DkEaL "]', page),
                "descripcion": extract_data('//div[@class="WeS02d fontBodyMedium"]//div[@class="PYvSYb "]', page),
            }
            results.append(data)
        
        browser.close()
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)

