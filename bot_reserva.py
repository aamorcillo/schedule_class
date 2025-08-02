# bot_reserva.py (versión para GitHub Actions)

import os
import time
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURACIÓN ---
# Los datos ahora se leen desde los "Secrets" de GitHub
USER_EMAIL = os.getenv("THFIT_USER")
USER_PASSWORD = os.getenv("THFIT_PASS")

TARGET_CLASS_NAME = "FIT CAMP"
TARGET_CLASS_TIME = "10:00"
TARGET_WEEKDAY = 2  # 0=Lunes, 1=Martes, 2=Miércoles, etc.
# --------------------

LOGIN_URL = "https://thfit.cl/reservar"

# (El resto de las funciones calculate_booking_time y run_booking_bot son iguales,
# pero run_booking_bot necesita la configuración del modo headless)

def run_booking_bot():
    """Inicia el proceso de automatización para reservar la clase."""
    
    booking_open_time, target_date = calculate_booking_time()

    print(f"✅ Bot configurado para la clase '{TARGET_CLASS_NAME}' del {target_date.strftime('%A, %d de %B')}.")
    print(f"⏳ El proceso de reserva comenzará automáticamente a las: {booking_open_time.strftime('%H:%M:%S del %A')}.")
    
    while datetime.now() < booking_open_time:
        print(f"Esperando... Hora actual: {datetime.now().strftime('%H:%M:%S')}", end='\r')
        time.sleep(30)

    print("\n💥 ¡Hora de reservar! Iniciando el navegador en modo headless...")
    
    # --- Configuración para modo headless en GitHub Actions ---
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # -----------------------------------------------------------

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 20)

    try:
        # El resto del código de la función es exactamente el mismo...
        print("1. Buscando el formulario de inicio de sesión...")
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)

        print("2. Ingresando credenciales...")
        email_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
        email_input.send_keys(USER_EMAIL)
        
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(USER_PASSWORD)
        
        driver.find_element(By.ID, "login-button").click()
        print("   -> Sesión iniciada.")
        
        wait.until(EC.presence_of_element_located((By.ID, "classSchedule-mainTable")))
        
        print("3. Navegando al día correcto...")
        today_on_calendar_str = driver.find_element(By.CLASS_NAME, "headText").get_attribute('textContent').strip()
        today_on_calendar = datetime.strptime(today_on_calendar_str, '%A, %B %d, %Y').date()
        
        while today_on_calendar < target_date:
            driver.find_element(By.CLASS_NAME, "primary-button--arrow-right").click()
            time.sleep(1)
            today_on_calendar_str = driver.find_element(By.CLASS_NAME, "headText").get_attribute('textContent').strip()
            today_on_calendar = datetime.strptime(today_on_calendar_str, '%A, %B %d, %Y').date()

        print(f"   -> Navegación exitosa al {target_date.strftime('%A, %d de %B')}.")

        print(f"4. Buscando la clase '{TARGET_CLASS_NAME}' a las {TARGET_CLASS_TIME}...")
        reserve_button_xpath = f"//tr[.//span[text()='{TARGET_CLASS_NAME}'] and .//span[contains(text(), '{TARGET_CLASS_TIME}')]]//input[contains(@value, 'Sign Up Now')]"
        reserve_button = wait.until(EC.element_to_be_clickable((By.XPATH, reserve_button_xpath)))

        print("   -> ¡Clase encontrada! Realizando la reserva...")
        reserve_button.click()
        
        print("\n🎉 ¡ÉXITO! Tu clase ha sido reservada (o el primer paso se completó).")

    except Exception as e:
        print(f"\n❌ ERROR: No se pudo completar la reserva. Motivo: {e}")
        driver.save_screenshot('error_screenshot.png') # Guarda una captura para depurar
    finally:
        print("Cerrando bot.")
        driver.quit()

# (La función calculate_booking_time se mantiene igual que en el script original)
def calculate_booking_time():
    now = datetime.now()
    days_ahead = (TARGET_WEEKDAY - now.weekday() + 7) % 7
    if days_ahead == 0 and now.hour >= int(TARGET_CLASS_TIME.split(':')[0]):
        days_ahead = 7
    target_class_date = now + timedelta(days=days_ahead)
    target_class_datetime = target_class_date.replace(hour=int(TARGET_CLASS_TIME.split(':')[0]), minute=0, second=0, microsecond=0)
    booking_open_time = target_class_datetime - timedelta(hours=36)
    return booking_open_time, target_class_datetime.date()

if __name__ == "__main__":
    if not USER_EMAIL or not USER_PASSWORD:
        print("❌ Error: Las credenciales THFIT_USER y THFIT_PASS no están configuradas en los Secrets de GitHub.")
    else:
        run_booking_bot()