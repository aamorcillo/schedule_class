# bot_reserva.py (versión final con tiempo de reserva parametrizable)

import os
import time
from datetime import datetime, timedelta
from math import ceil

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURACIÓN ---
# Lista de nombres de clase a buscar.
TARGET_CLASS_NAMES = ["FIT CAMP", "BOX-FIT", "FULL BODY"]
TARGET_CLASS_TIME = "10:00"

# ¡NUEVO! Define con cuántas horas de antelación se abren las reservas.
# Ejemplos: 36 para thfit.cl, 24 si fuera un día antes, etc.
BOOKING_WINDOW_HOURS = 27

# Credenciales desde los Secrets de GitHub
USER_EMAIL = os.getenv("THFIT_USER")
USER_PASSWORD = os.getenv("THFIT_PASS")
# --------------------

LOGIN_URL = "https://thfit.cl/reservar"

def get_target_date():
    """
    Calcula la fecha objetivo basándose en las horas de antelación.
    Ej: 24h -> mañana (1 día). 36h -> pasado mañana (2 días).
    """
    days_to_look_ahead = ceil(BOOKING_WINDOW_HOURS / 24)
    target_date = (datetime.now() + timedelta(days=days_to_look_ahead)).date()
    return target_date

def run_booking_bot():
    """Inicia el proceso de automatización para reservar la clase."""
    
    target_date = get_target_date()

    print(f"✅ Bot configurado para buscar clases el día: {target_date.strftime('%A, %d de %B')}.", flush=True)
    print(f"⏳ Buscando una de las clases: {TARGET_CLASS_NAMES} a las {TARGET_CLASS_TIME}.", flush=True)
    print(f"   (Considerando una ventana de reserva de {BOOKING_WINDOW_HOURS} horas)", flush=True)
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(LOGIN_URL)
        print("1. Buscando el formulario de inicio de sesión...", flush=True)
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)

        print("2. Ingresando credenciales...", flush=True)
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USER_EMAIL)
        driver.find_element(By.ID, "password").send_keys(USER_PASSWORD)
        driver.find_element(By.ID, "login-button").click()
        print("   -> Sesión iniciada.", flush=True)
        
        wait.until(EC.presence_of_element_located((By.ID, "classSchedule-mainTable")))
        
        print(f"3. Navegando hasta el día {target_date.strftime('%A, %d de %B')}...", flush=True)
        
        while True:
            current_date_str = driver.find_element(By.CLASS_NAME, "headText").get_attribute('textContent').strip()
            current_date = datetime.strptime(current_date_str, '%A, %B %d, %Y').date()
            if current_date >= target_date:
                print(f"   -> Navegación exitosa.", flush=True)
                break
            driver.find_element(By.CLASS_NAME, "primary-button--arrow-right").click()
            time.sleep(1)

        class_found = False
        for class_name in TARGET_CLASS_NAMES:
            try:
                print(f"   -> Intentando con '{class_name}'...", flush=True)
                reserve_button_xpath = f"//tr[.//span[text()='{class_name}'] and .//span[contains(text(), '{TARGET_CLASS_TIME}')]]//input[contains(@value, 'Sign Up Now')]"
                reserve_button = driver.find_element(By.XPATH, reserve_button_xpath)
                
                if reserve_button.is_enabled():
                    print(f"   -> ¡Clase '{class_name}' encontrada! Realizando la reserva...", flush=True)
                    reserve_button.click()
                    class_found = True
                    break
                else:
                    print(f"   -> Clase '{class_name}' encontrada pero no se puede reservar.", flush=True)
            except NoSuchElementException:
                print(f"   -> Clase '{class_name}' no encontrada.", flush=True)
                continue

        if class_found:
            print("\n🎉 ¡ÉXITO! Tu clase ha sido reservada.", flush=True)
        else:
            print("\n❌ FALLO: No se encontró ninguna de las clases deseadas o no estaban disponibles.", flush=True)

    except Exception as e:
        print(f"\n❌ ERROR GENERAL: No se pudo completar la reserva. Motivo: {e}", flush=True)
        driver.save_screenshot('error_screenshot.png')
    finally:
        print("Cerrando bot.", flush=True)
        driver.quit()

if __name__ == "__main__":
    if not USER_EMAIL or not USER_PASSWORD:
        print("❌ Error: Las credenciales THFIT_USER y THFIT_PASS no están configuradas en los Secrets de GitHub.", flush=True)
    else:
        run_booking_bot()