Bot de Reservas para Gimnasio (thfit.cl)
Este es un bot de automatización diseñado para reservar clases en el sitio web thfit.cl. Utiliza Python con Selenium para imitar el comportamiento de un usuario y se ejecuta de manera automática y programada utilizando GitHub Actions, asegurando un cupo en clases de alta demanda como "FIT CAMP".

✨ Características
Reserva Automatizada: Navega, inicia sesión y reserva la clase deseada sin intervención manual.

Ejecución Programada: Gracias a GitHub Actions, el bot se activa automáticamente a la hora precisa para realizar la reserva.

Seguridad de Credenciales: Tu usuario y contraseña se almacenan de forma segura utilizando GitHub Secrets, no directamente en el código.

Operación Headless: El navegador se ejecuta en un servidor en segundo plano, sin necesidad de una interfaz gráfica ni de tener tu PC encendido.

Configurable: Puedes ajustar fácilmente la clase, la hora y el día de la semana que deseas reservar.

🚀 Configuración Inicial
Sigue estos pasos para poner en marcha el bot.

1. Clona o Prepara tu Repositorio
Asegúrate de tener este repositorio configurado como privado en tu cuenta de GitHub para proteger la lógica y el acceso.

2. Configura los Secrets de GitHub
Para que el bot pueda iniciar sesión de forma segura, debes almacenar tus credenciales en los "Secrets" del repositorio.

En este repositorio, ve a la pestaña Settings.

En el menú de la izquierda, navega a Secrets and variables > Actions.

Haz clic en New repository secret y crea los siguientes dos secrets:

Nombre: THFIT_USER

Valor: Tu correo electrónico de inicio de sesión (ej: arturo.morcillo@live.cl).

Nombre: THFIT_PASS

Valor: Tu contraseña real para thfit.cl.

3. Personaliza la Reserva (Opcional)
Si quieres cambiar la clase o el día a reservar, edita las siguientes líneas en el archivo bot_reserva.py:

Python

# bot_reserva.py

# ...
TARGET_CLASS_NAME = "FIT CAMP"
TARGET_CLASS_TIME = "10:00"

# Día de la semana (0=Lunes, 1=Martes, 2=Miércoles, 3=Jueves, etc.)
TARGET_WEEKDAY = 2 
# ...
4. Revisa el Horario de Ejecución
El bot se ejecuta según un horario definido en el archivo .github/workflows/booking.yml.

YAML

# .github/workflows/booking.yml
# ...
  schedule:
    # Ejecuta el bot todos los días a las 01:55 AM UTC.
    - cron: '55 1 * * *'
# ...
cron: '55 1 * * *' significa que la tarea se ejecutará a la 01:55 UTC.

Las reservas para las clases de las 10:00 AM se abren 36 horas antes, es decir, a las 22:00 del ante-día.

La hora 01:55 UTC corresponde a las 21:55 en Chile continental (UTC-4). Esto le da al bot 5 minutos para iniciarse antes de que las reservas se abran a las 22:00.

Nota: Si Chile cambia de huso horario (horario de verano), puede que necesites ajustar la hora UTC en este archivo.

⚙️ Cómo Funciona
Activación Programada: GitHub Actions activa el flujo de trabajo (workflow) a la hora definida en el archivo booking.yml.

Preparación del Entorno: Se crea un entorno virtual en un servidor de Ubuntu, se instala Python y las dependencias (selenium, webdriver-manager).

Ejecución del Script: Se ejecuta el script bot_reserva.py. Las credenciales se inyectan de forma segura desde los GitHub Secrets.

Automatización: Selenium inicia un navegador Chrome en modo headless (sin pantalla).

Proceso de Reserva: El bot navega a thfit.cl, maneja el iframe de inicio de sesión, introduce tus credenciales, navega hasta el día correcto y hace clic en el botón de reserva de la clase especificada.

Finalización: El bot cierra la sesión. Puedes revisar el resultado en los logs de la ejecución.

🛠️ Uso y Monitoreo
Ejecución Automática
El bot se ejecutará sin que tengas que hacer nada, según el horario cron.

Ejecución Manual
Si quieres probar el bot o forzar una reserva, puedes ejecutarlo manualmente:

Ve a la pestaña Actions de tu repositorio.

En el menú de la izquierda, haz clic en "Bot de Reserva de Clases".

Verás un botón que dice "Run workflow". Haz clic en él para iniciar el bot al instante.

Verificación de Logs
Para ver si la reserva fue exitosa o si ocurrió un error:

Ve a la pestaña Actions.

Haz clic en la ejecución más reciente del workflow.

Selecciona el job llamado book_class.

Expande los pasos para ver los mensajes impresos por el script. Si ocurre un error, aquí encontrarás los detalles y una captura de pantalla del fallo (error_screenshot.png) que se puede descargar desde los "Artifacts" de la ejecución.

📄 Licencia
Este proyecto es de uso personal. Se distribuye bajo la Licencia MIT.
