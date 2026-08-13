# 🧟‍♂️ Project Zomboid Discord Bot

Un bot de Discord en Python diseñado para administrar y monitorear un servidor dedicado de **Project Zomboid** en Linux (Ubuntu/Debian). Permite ver el estado en tiempo real, listar jugadores en línea y gestionar el servidor (iniciar, apagar, reiniciar) mediante sesiones de `screen`.

---

## 📋 Requisitos Previos

1. **Sistema Operativo Linux:** El bot utiliza herramientas de sistema como `screen` y `tail`.
2. **GNU Screen:** El servidor de Project Zomboid debe ejecutarse en una sesión `screen`.
3. **Python 3.8+** instalado.
4. **Librería de Discord:**
   ```bash
   pip install discord.py

⚙️ Paso 1: Configurar el Bot en Discord Developer Portal
Entra a Discord Developer Portal y crea una New Application.

En la pestaña Bot, presiona Reset Token para obtener tu Token.

En la sección Privileged Gateway Intents, activa:

✅ Server Members Intent

✅ Message Content Intent

Para invitar el bot a tu servidor:

Ve a OAuth2 -> URL Generator.

En Scopes, selecciona bot.

En Bot Permissions, asigna: Send Messages, Read Messages/View Channels y Embed Links.

Copia la URL generada y abre el enlace en tu navegador para autorizarlo.

## 📂 Paso 2: Estructura de Archivos

Crea una carpeta en tu servidor y coloca los archivos `config.json` y `bot.py`:

```text
pzbot/
├── config.json
└── bot.py
```

1. Archivo config.json
Crea el archivo config.json con la siguiente estructura:

```text
{
    "TOKEN": "TU_TOKEN_DE_DISCORD_AQUI",
    "COMMAND_PREFIX": "!pz ",
    "SERVER_NAME": "Project Zomboid",
    "SCREEN_NAME": "Zomboid",
    "PUERTO_SERVIDOR": 16261,

    "START_COMMAND": "screen -dmS Zomboid /home/usuario/Zomboid/start-server.sh",
    "STOP_COMMAND": "screen -S Zomboid -p 0 -X stuff \"quit$(printf '\\r')\"",
    "LOG_FILE_PATH": "/home/usuario/Zomboid/server-console.txt",

    "STATUS_UPDATE_SECONDS": 15,
    "PLAYER_QUERY_DELAY": 0.5,

    "ADMIN_ROLES": [
        "Owner",
        "IT ADMIN",
        "Admin"
    ],
    "UPDATE_COMMAND": "steamcmd +runscript update_zomboid.txt"
}
```

### 🛠️ Explicación de los Parámetros del Configuración (`config.json`)

* **`TOKEN`**: Tu token secreto obtenido en el Discord Developer Portal.
* **`COMMAND_PREFIX`**: Prefijo para invocar los comandos del bot (ejemplo: `!pz `).
* **`SERVER_NAME`**: Nombre personalizado de tu servidor que se mostrará en las respuestas del bot.
* **`SCREEN_NAME`**: Nombre de la sesión `screen` de Linux donde se ejecuta tu servidor de PZ.
* **`PUERTO_SERVIDOR`**: Puerto UDP/IP del servidor (por defecto `16261`).
* **`START_COMMAND`**: Ruta y comando ejecutable para iniciar el servidor dentro de `screen`.
* **`STOP_COMMAND`**: Comando encargado de enviar `quit` a la consola del servidor para guardar y apagar de forma segura.
* **`LOG_FILE_PATH`**: Ruta exacta al archivo `server-console.txt` del servidor para extraer la cantidad de usuarios conectados.
* **`STATUS_UPDATE_SECONDS`**: Frecuencia (en segundos) con la que el bot actualiza la actividad en Discord.
* **`ADMIN_ROLES`**: Lista de roles de Discord con permisos para ejecutar comandos de administración (`iniciar`, `apagar`, `reiniciar`).

  ---

## 🚀 Paso 3: Ejecución del Bot

Una vez guardados los archivos `config.json` y `bot.py` en la misma carpeta, puedes probar el bot ejecutando:

```bash
python3 bot.py
```

Si todo está bien configurado, verás el mensaje de confirmación en tu consola:

```text
--------------------------------
Bot conectado como TuBot#1234
Desarrollado por: Osvaldo De Los Santos
--------------------------------
```

💡 Mantener el Bot corriendo 24/7 en segundo plano

Para evitar que el bot se apague al cerrar tu terminal SSH, es recomendable ejecutarlo dentro de su propia sesión de screen o mediante un servicio de systemd.

## Con GNU Screen

```text
# 1. Crear una nueva sesión independiente para el bot
screen -S pzbot

# 2. Iniciar el bot dentro de la sesión
python3 bot.py

# 3. Salir de la sesión sin apagar el bot:
# Presiona CTRL + A y luego la tecla D
```
