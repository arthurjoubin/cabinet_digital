from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time
import os
from io import BytesIO

def capture_website_scroll(url, output_path):
    # S'assurer que le dossier parent existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Configuration de Chrome en mode headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        time.sleep(3)  # Attendre le chargement
        
        # Tenter de fermer différents types de popups de cookies
        try:
            # Boutons communs pour les popups de cookies
            selectors = [
                '#cookieConsent button', 
                '.cookie-banner button',
                '#onetrust-accept-btn-handler',
                '.cookie-notice button',
                'button[data-cookiebanner="accept"]',
                '.cookies-accept',
                '#didomi-notice-agree-button',
                '.cookie-consent button'
            ]
            
            for selector in selectors:
                try:
                    button = driver.find_element('css selector', selector)
                    button.click()
                    time.sleep(0.5)
                    break
                except:
                    continue
        except:
            pass  # Continue si aucun popup n'est trouvé
            
        # Vérifier le code de statut HTTP
        navigation_entry = driver.execute_script("return window.performance.getEntries()[0]")
        if "responseStatus" in navigation_entry and navigation_entry["responseStatus"] == 403:
            print(f"Accès refusé (403) pour {url}")
            return False
            
        # Obtenir la hauteur totale
        total_height = driver.execute_script("return document.body.scrollHeight")
        
        # Capturer des images pendant le scroll
        frames = []
        current_position = 0
        scroll_step = 300
        
        while current_position < total_height:
            # Scroll
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(0.5)
            
            # Capture
            screenshot = driver.get_screenshot_as_png()
            image = Image.open(BytesIO(screenshot))
            frames.append(image)
            
            current_position += scroll_step
            
        # Sauvegarder en GIF
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=1000,
            loop=0
        )
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la capture: {e}")
        return False
    finally:
        driver.quit() 