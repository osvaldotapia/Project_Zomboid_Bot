import discord
from discord.ext import commands, tasks
import subprocess
import json

# 🔍 Cargar configuración
# Ruta del archivo config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

TOKEN = config["TOKEN"]
COMMAND_PREFIX = config["COMMAND_PREFIX"]
ADMIN_ROLES = config["ADMIN_ROLES"]  # Ahora es una lista de roles
PUERTO_SERVIDOR = config["PUERTO_SERVIDOR"]
START_COMMAND = config["START_COMMAND"]
STOP_COMMAND = config["STOP_COMMAND"]
LOG_FILE_PATH = "/root/Zomboid/server-console.txt"

# Habilitar los intents necesarios
intents = discord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# 🔎 Función para obtener la cantidad de jugadores conectados
def obtener_jugadores():
    try:
        with open(LOG_FILE_PATH, "r") as log_file:
            logs = log_file.readlines()

        conexiones = [line for line in logs if "Connected new client" in line]
        desconexiones = [line for line in logs if "Disconnected player" in line]

        jugadores_conectados = len(conexiones) - len(desconexiones)

        return jugadores_conectados

    except Exception as e:
        print(f"Error al leer el archivo de log: {e}")
        return 0

# 🔄 Tarea en segundo plano que actualiza el estado del bot cada 60 segundos
@tasks.loop(seconds=60)
async def actualizar_estado():
    jugadores = obtener_jugadores()
    actividad = discord.Game(f"🎮 {jugadores} jugadores conectados")
    await bot.change_presence(activity=actividad)

# 🚀 Evento cuando el bot está listo
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    actualizar_estado.start()

# 🔁 Comando para reiniciar el servidor
@bot.command()
async def reiniciar(ctx):
    user_roles = [role.name for role in ctx.author.roles]  

    if any(role in ADMIN_ROLES for role in user_roles):  
        await ctx.send("♻️ Reiniciando servidor de Project Zomboid...")

        subprocess.run(STOP_COMMAND, shell=True)
        subprocess.run(START_COMMAND, shell=True)

        await ctx.send("✅ Servidor reiniciado con éxito.")
    else:
        await ctx.send("🚫 No tienes permisos para reiniciar el servidor.")

# 🔥 Iniciar el bot
bot.run(TOKEN)
