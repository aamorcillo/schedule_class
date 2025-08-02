# bot_reserva.py (versión final con "disfraz" de navegador)

import os
import sys
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
TARGET_CLASS_NAMES = ["FIT CAMP", "BOX-FIT", "FULL BODY"]
TARGET_CLASS_TIME = "10:00"
BOOKING_WINDOW_HOURS = 27
BOOKING_OPEN_TIME_LOCAL = 10

USER_EMAIL = os.getenv("THFIT_USER")
USER_PASSWORD = os.getenv("THFIT_PASS")
# --------------------

LOGIN_URL = "https://thfit.cl/reservar"

def get_target_date():
    days_to_look_ahead = ceil(BOOKING_WINDOW_HOURS / 24)
    target_date = (datetime.now() + timedelta(days=days_to_look_ahead)).date()
    return target_date

def run_booking_bot():
    now = datetime.now()
    booking_time_today = now.replace(hour=BOOKING_OPEN_TIME_LOCAL, minute=0, second=0, microsecond=0)

    print(f"✅ Bot iniciado a las {now.strftime('%H:%M:%S')}.")
    if now < booking_time_today:
        print(f"⏳ Esperando hasta las {booking_time_today.strftime('%H:%M:%S')} para iniciar la reserva...")
        while datetime.now() < booking_time_today:
            remaining = booking_time_today - datetime.now()
            print(f"   -> Tiempo restante: {str(remaining).split('.')[0]}", flush=True)
            time.sleep(30)
    
    print("\n💥 ¡Hora de reservar! Configurando el navegador...", flush=True)
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # --- NUEVO "DISFRAZ" ---
    # Hacemos que el bot se presente como un navegador Chrome normal de Windows.
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
    
    print("   -> Opciones de Chrome configuradas. Intentando iniciar el driver...", flush=True)
    driver = None
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        print("   -> ¡Driver iniciado con éxito!", flush=True)
        wait = WebDriverWait(driver, 20)
        
        print("   -> Intentando cargar la URL del sitio...", flush=True)
        driver.get(LOGIN_URL)
        print("   -> ¡URL cargada con éxito!", flush=True)

        print("1. Buscando el formulario de inicio de sesión...", flush=True)
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)

        print("2. Ingresando credenciales...", flush=True)
        # ... el resto del código es idéntico ...
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USER_EMAIL)
        driver.find_element(By.ID, "password").send_keys(USER_PASSWORD)
        driver.find_element(By.ID, "login-button").click()
        print("   -> Sesión iniciada.", flush=True)
        
        wait.until(EC.presence_of_element_located((By.ID, "classSchedule-mainTable")))
        
        target_date = get_target_date()
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
        print(f"\n❌ ERROR GENERAL: No se pudo completar la reserva. Motivo: {str(e)}", flush=True)
        if driver:
            driver.save_screenshot('error_screenshot.png')
    finally:
        print("Cerrando bot.", flush=True)
        if driver:
            driver.quit()

if __name__ == "__main__":
    log_file = open("bot_log.txt", "w")
    original_stdout = sys.stdout
    sys.stdout = log_file
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("====================================================")
        print(f"== INICIO DEL SCRIPT: {now_str} ==")
        print("====================================================")
        if not USER_EMAIL or not USER_PASSWORD:
            print("❌ Error: Las credenciales THFIT_USER y THFIT_PASS no están configuradas en los Secrets de GitHub.")
        else:
            run_booking_bot()
    finally:
        print("\n====================================================")
        print("== FIN DEL SCRIPT ==")
        print("====================================================")
        sys.stdout = original_stdout
        log_file.close()