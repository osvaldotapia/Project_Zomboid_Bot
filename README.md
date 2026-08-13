# 🧟‍♂️ Project Zomboid Discord Bot

Un bot de Discord en Python para administrar y monitorear un servidor dedicado de **Project Zomboid** en sistemas Linux (Ubuntu/Debian). Permite ver el estado en tiempo real, listar jugadores conectados y ejecutar comandos de consola (iniciar, apagar, reiniciar) mediante sesiones de `screen`.

---

## 📋 Requisitos Previos

1. **Sistema Operativo Linux:** El bot utiliza utilidades de consola como `screen` y `tail`.
2. **GNU Screen:** El servidor de Project Zomboid debe ejecutarse dentro de una sesión `screen`.
3. **Python 3.8+** instalado en el servidor.
4. **Librerías de Python:**
   ```bash
   pip install discord.py

   ⚙️ Paso 1: Configurar el Bot en Discord Developer Portal
Ve a Discord Developer Portal y crea una New Application.

Dirígete a la sección Bot y presiona Reset Token para obtener tu Token de acceso.

En esa misma pestaña, desplázate hacia Privileged Gateway Intents y activa las siguientes opciones:

✅ Server Members Intent
✅ Message Content Intent

Para invitar al bot a tu servidor de Discord:
Ve a OAuth2 -> URL Generator.
En Scopes, marca bot.

En Bot Permissions, asigna permisos de lectura y envío de mensajes (Send Messages, Read Messages/View Channels, Embed Links).

📂 Paso 2: Estructura del Proyecto
Crea una carpeta en tu servidor (por ejemplo, /home/usuario/pzbot/) y coloca los dos archivos principales:

Plaintext
pzbot/
├── config.json
└── bot.py

Copia la URL generada y ábrela en tu navegador para autorizar al bot.
