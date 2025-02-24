from playwright.sync_api import sync_playwright
import json
import argparse
import time

def extract_data(xpath, page):
    return page.locator(xpath).first.inner_text() if page.locator(xpath).count() > 0 else ""

def main(search_for, total):
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', headless=False)
        page = browser.new_page()

        # Abrir Google Maps
        page.goto("https://www.google.com/maps/@32.9817464,70.1930781,3.67z?&hl=es&gl=ES", timeout=60000)
        #                                       Latitud     Longitud   Zoom minimo de 10km  idioma  pais
        page.wait_for_timeout(1000)

        # Aceptar las cookies
        accept_button = page.locator('//button[@aria-label="Aceptar todo"]').first
        if accept_button.count() > 0:
            accept_button.click()
            page.wait_for_timeout(1000)

        # hacer la busqueda
        page.locator('//input[@id="searchboxinput"]').fill(search_for)
        page.keyboard.press("Enter")
        page.wait_for_selector('//a[contains(@href, "https://www.google.com/maps/place")]')

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



            #time.sleep(500000)


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

                    close_button = page.locator('//span[@class="G6JA1c google-symbols"]').first
                    if close_button.count() > 0:
                        close_button.click()
                        page.wait_for_timeout(500)
                else:
                    short_url = ""

                 
            # Step 4: Open the short URL in a new Playwright context (to prevent losing the original page)
                if short_url:
                    context = page.context.new_page()  # Open a new tab
                    context.goto(short_url, timeout=10000)
                    page.wait_for_timeout(1500)  # Allow the page to load

                    # Extract the image from the meta tag
                    meta_image = context.locator('//meta[@itemprop="image"]').first
                    image_url = meta_image.get_attribute("content") if meta_image.count() > 0 else ""

                    # Close the new tab after extracting the image
                    context.close()
                else:
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
        print(json.dumps(results, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str, default="pizza")
    parser.add_argument("-t", "--total", type=int, default=20)
    args = parser.parse_args()

    main(args.search, args.total)
