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
