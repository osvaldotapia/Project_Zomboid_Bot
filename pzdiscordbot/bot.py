import discord
from discord.ext import commands, tasks

import json
import subprocess
import os
import re
import asyncio


# ============================================================
# CONFIGURACION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CONFIG_FILE = os.path.join(
    BASE_DIR,
    "config.json"
)


with open(
    CONFIG_FILE,
    "r",
    encoding="utf-8"
) as archivo:

    config = json.load(archivo)


# Todo se obtiene desde config.json

TOKEN = config["TOKEN"]

PREFIX = config["COMMAND_PREFIX"]

SERVER_NAME = config["SERVER_NAME"]

SCREEN_NAME = config["SCREEN_NAME"]

PUERTO_SERVIDOR = config["PUERTO_SERVIDOR"]

START_COMMAND = config["START_COMMAND"]

STOP_COMMAND = config["STOP_COMMAND"]

LOG_FILE_PATH = config["LOG_FILE_PATH"]

STATUS_UPDATE_SECONDS = config["STATUS_UPDATE_SECONDS"]

PLAYER_QUERY_DELAY = config["PLAYER_QUERY_DELAY"]

ADMIN_ROLES = config["ADMIN_ROLES"]

UPDATE_COMMAND = config.get(
    "UPDATE_COMMAND",
    ""
)


# ============================================================
# DISCORD
# ============================================================

intents = discord.Intents.default()

intents.message_content = True

intents.members = True


bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)


# ============================================================
# VARIABLES
# ============================================================

ultimo_estado = "DESCONOCIDO"

# ============================================================
# ESTADO DE ACTUALIZACION
# ============================================================

actualizacion_en_curso = False
actualizacion_lock = asyncio.Lock()


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def screen_activo():

    """
    Comprueba si existe la sesión screen del servidor.
    """

    try:

        resultado = subprocess.run(
            [
                "screen",
                "-S",
                SCREEN_NAME,
                "-Q",
                "select",
                "."
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return resultado.returncode == 0

    except Exception as error:

        print(
            f"❌ Error comprobando screen: {error}"
        )

        return False


def servidor_encendido():

    """
    Comprueba si la sesión screen del servidor está activa.
    """

    return screen_activo()


def ejecutar_comando(comando):

    """
    Ejecuta un comando definido en config.json.
    """

    if not comando:

        print(
            "❌ Comando no configurado."
        )

        return False


    try:

        resultado = subprocess.run(
            comando,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


        if resultado.returncode != 0:

            print(
                "❌ Error ejecutando comando:"
            )

            print(
                resultado.stderr
            )

            return False


        return True


    except Exception as error:

        print(
            f"❌ Error ejecutando comando: {error}"
        )

        return False


# ============================================================
# LEER JUGADORES ACTUALES DE PROJECT ZOMBOID
# ============================================================

def obtener_jugadores():

    """
    Envía 'players' directamente a la consola de Project Zomboid
    y lee la respuesta más reciente del log.

    Devuelve una lista de jugadores ficticia:
        Jugador 1
        Jugador 2
        ...

    La cantidad es la cantidad REAL reportada por PZ.
    """

    jugadores = []


    # Primero comprobamos que el servidor esté realmente activo.

    if not screen_activo():

        return jugadores


    try:

        # ----------------------------------------------------
        # Enviar "players" a la consola PZ
        # ----------------------------------------------------

        comando = (
            f'screen -S "{SCREEN_NAME}" '
            f'-p 0 -X stuff "players$(printf \'\\r\')"'
        )


        resultado_comando = subprocess.run(
            comando,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


        if resultado_comando.returncode != 0:

            print(
                "❌ No se pudo enviar el comando players."
            )

            return jugadores


        # ----------------------------------------------------
        # Esperar respuesta del servidor
        # ----------------------------------------------------

        import time

        time.sleep(
            PLAYER_QUERY_DELAY
        )


        # ----------------------------------------------------
        # Leer las últimas líneas del log
        # ----------------------------------------------------

        resultado = subprocess.run(
            [
                "tail",
                "-30",
                LOG_FILE_PATH
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )


        if resultado.returncode != 0:

            print(
                f"❌ Error leyendo log: {resultado.stderr}"
            )

            return jugadores


        lineas = resultado.stdout.splitlines()


        # ----------------------------------------------------
        # Buscar la respuesta MÁS RECIENTE
        # ----------------------------------------------------

        for linea in reversed(lineas):

            coincidencia = re.search(
                r"Players connected \((\d+)\):",
                linea
            )


            if coincidencia:

                cantidad = int(
                    coincidencia.group(1)
                )


                # PZ dice 0

                if cantidad <= 0:

                    return []


                # Creamos la lista según la cantidad real

                for numero in range(
                    1,
                    cantidad + 1
                ):

                    jugadores.append(
                        f"Jugador {numero}"
                    )


                return jugadores


    except Exception as error:

        print(
            f"❌ Error obteniendo jugadores: {error}"
        )


    return jugadores


# ============================================================
# PERMISOS ADMIN
# ============================================================

def es_admin(ctx):

    if ctx.author.guild_permissions.administrator:

        return True


    for rol in ctx.author.roles:

        if rol.name in ADMIN_ROLES:

            return True


    return False


# ============================================================
# ESPERAR A QUE EL SERVIDOR SE APAGUE
# ============================================================

async def esperar_servidor_apagado(
    timeout=60
):

    """
    Espera hasta que la sesión screen de PZ desaparezca.

    Devuelve True si se apagó correctamente.
    Devuelve False si supera el tiempo máximo.
    """

    tiempo = 0


    while tiempo < timeout:

        if not screen_activo():

            return True


        await asyncio.sleep(1)

        tiempo += 1


    return False


# ============================================================
# ESPERAR A QUE EL SERVIDOR ARRANQUE
# ============================================================

async def esperar_servidor_arranque(
    timeout=60
):

    """
    Espera hasta que aparezca la sesión screen de PZ.
    """

    tiempo = 0


    while tiempo < timeout:

        if screen_activo():

            return True


        await asyncio.sleep(1)

        tiempo += 1


    return False


# ============================================================
# READY
# ============================================================

@bot.event
async def on_ready():
    COLOR_ROJO = "\033[91m"
    COLOR_AZUL = "\033[94m"
    COLOR_RESET = "\033[0m"

    print("--------------------------------")
    print(f"Bot conectado como {bot.user}")
    print(f"{COLOR_ROJO}Desarrollado por: {COLOR_AZUL}Osvaldo De Los Santos{COLOR_RESET}")
    print("--------------------------------")

    if not actualizar_estado.is_running():
        actualizar_estado.start()


# ============================================================
# HELP
# ============================================================

@bot.command(
    name="help"
)
async def ayuda(ctx):

    embed = discord.Embed(
        title="🤖 Project Zomboid Bot",
        description="Comandos disponibles",
        color=discord.Color.green()
    )


    embed.add_field(
        name=f"{PREFIX}help",
        value="Muestra esta ayuda.",
        inline=False
    )


    embed.add_field(
        name=f"{PREFIX}jugadores",
        value="Muestra los jugadores conectados.",
        inline=False
    )


    embed.add_field(
        name=f"{PREFIX}estado",
        value="Muestra el estado real del servidor.",
        inline=False
    )


    embed.add_field(
        name=f"{PREFIX}iniciar",
        value="Inicia el servidor. (Admin)",
        inline=False
    )


    embed.add_field(
        name=f"{PREFIX}apagar",
        value="Guarda y apaga el servidor. (Admin)",
        inline=False
    )


    embed.add_field(
        name=f"{PREFIX}reiniciar",
        value="Guarda, apaga y vuelve a iniciar el servidor. (Admin)",
        inline=False
    )

    embed.add_field(
        name=f"{PREFIX}actualizar",
        value="Actualiza el servidor mediante SteamCMD. (Admin)",
        inline=False
    )


    await ctx.send(
        embed=embed
    )


# ============================================================
# JUGADORES
# ============================================================

@bot.command(
    name="jugadores"
)
async def jugadores(ctx):

    lista = obtener_jugadores()


    if not servidor_encendido():

        await ctx.send(
            "🔴 El servidor está apagado."
        )

        return


    if not lista:

        await ctx.send(
            "👥 No hay jugadores conectados."
        )

        return


    texto = "\n".join(
        [
            f"🟢 {jugador}"
            for jugador in lista
        ]
    )


    embed = discord.Embed(
        title="👥 Jugadores Online",
        description=texto,
        color=discord.Color.blue()
    )


    embed.set_footer(
        text=f"Total: {len(lista)} jugadores"
    )


    await ctx.send(
        embed=embed
    )


# ============================================================
# ESTADO DEL SERVIDOR
# ============================================================

@bot.command(
    name="estado"
)
async def estado(ctx):

    servidor = servidor_encendido()


    if not servidor:

        estado_servidor = "🔴 OFFLINE"

        cantidad = 0

    else:

        jugadores = obtener_jugadores()

        cantidad = len(jugadores)

        estado_servidor = "🟢 ONLINE"


    embed = discord.Embed(
        title=f"🎮 {SERVER_NAME}",
        color=(
            discord.Color.green()
            if servidor
            else discord.Color.red()
        )
    )


    embed.add_field(
        name="Estado",
        value=estado_servidor,
        inline=False
    )


    embed.add_field(
        name="Jugadores",
        value=str(cantidad),
        inline=False
    )


    embed.add_field(
        name="Puerto",
        value=str(PUERTO_SERVIDOR),
        inline=False
    )


    await ctx.send(
        embed=embed
    )


# ============================================================
# INICIAR SERVIDOR
# ============================================================

@bot.command(
    name="iniciar"
)
async def iniciar(ctx):

    if not es_admin(ctx):

        await ctx.send(
            "🚫 No tienes permisos para iniciar el servidor."
        )

        return


    if servidor_encendido():

        await ctx.send(
            "⚠️ El servidor ya está iniciado."
        )

        return


    mensaje = await ctx.send(
        "🚀 Iniciando servidor Project Zomboid..."
    )


    resultado = ejecutar_comando(
        START_COMMAND
    )


    if not resultado:

        await mensaje.edit(
            content="❌ Error ejecutando el comando de inicio."
        )

        return


    iniciado = await esperar_servidor_arranque(
        60
    )


    if iniciado:

        await mensaje.edit(
            content="✅ Servidor iniciado correctamente."
        )

    else:

        await mensaje.edit(
            content="⚠️ El comando de inicio fue ejecutado, pero no se detectó la sesión screen."
        )


# ============================================================
# APAGAR SERVIDOR
# ============================================================

@bot.command(
    name="apagar"
)
async def apagar(ctx):

    if not es_admin(ctx):

        await ctx.send(
            "🚫 No tienes permisos para apagar el servidor."
        )

        return


    if not servidor_encendido():

        await ctx.send(
            "⚠️ El servidor ya está apagado."
        )

        return


    mensaje = await ctx.send(
        "🛑 Enviando `quit` al servidor para guardar y apagar..."
    )


    resultado = ejecutar_comando(
        STOP_COMMAND
    )


    if not resultado:

        await mensaje.edit(
            content="❌ No se pudo enviar el comando de apagado."
        )

        return


    apagado = await esperar_servidor_apagado(
        60
    )


    if apagado:

        await mensaje.edit(
            content="✅ Servidor guardado y apagado correctamente."
        )

    else:

        await mensaje.edit(
            content="⚠️ Se envió `quit`, pero el servidor todavía aparece activo."
        )


# ============================================================
# REINICIAR SERVIDOR
# ============================================================

@bot.command(
    name="reiniciar"
)
async def reiniciar(ctx):

    if not es_admin(ctx):

        await ctx.send(
            "🚫 No tienes permisos para reiniciar el servidor."
        )

        return


    mensaje = await ctx.send(
        "♻️ Iniciando reinicio del servidor..."
    )


    # --------------------------------------------------------
    # COMPROBAR SI ESTÁ ENCENDIDO
    # --------------------------------------------------------

    if servidor_encendido():

        await mensaje.edit(
            content=(
                "🛑 Enviando `quit` al servidor "
                "para guardar la partida..."
            )
        )


        # ----------------------------------------------------
        # ENVIAR QUIT
        # ----------------------------------------------------

        apagado_comando = ejecutar_comando(
            STOP_COMMAND
        )


        if not apagado_comando:

            await mensaje.edit(
                content=(
                    "❌ No se pudo enviar el comando "
                    "`quit` al servidor."
                )
            )

            return


        # ----------------------------------------------------
        # ESPERAR APAGADO REAL
        # ----------------------------------------------------

        await mensaje.edit(
            content=(
                "💾 Guardando partida y esperando "
                "a que el servidor termine..."
            )
        )


        apagado = await esperar_servidor_apagado(
            90
        )


        if not apagado:

            await mensaje.edit(
                content=(
                    "❌ El servidor no terminó de apagarse "
                    "dentro del tiempo esperado. "
                    "No se iniciará otro servidor."
                )
            )

            return


    else:

        await mensaje.edit(
            content=(
                "ℹ️ El servidor ya estaba apagado. "
                "Iniciándolo..."
            )
        )


    # --------------------------------------------------------
    # PAUSA ANTES DE ARRANCAR
    # --------------------------------------------------------

    await asyncio.sleep(3)


    # --------------------------------------------------------
    # INICIAR SERVIDOR
    # --------------------------------------------------------

    await mensaje.edit(
        content=(
            "🚀 Iniciando nuevamente "
            "Project Zomboid..."
        )
    )


    iniciado_comando = ejecutar_comando(
        START_COMMAND
    )


    if not iniciado_comando:

        await mensaje.edit(
            content="❌ Error ejecutando el comando de inicio."
        )

        return


    # --------------------------------------------------------
    # ESPERAR A QUE APAREZCA SCREEN
    # --------------------------------------------------------

    iniciado = await esperar_servidor_arranque(
        90
    )


    if iniciado:

        await mensaje.edit(
            content=(
                "✅ Servidor reiniciado correctamente."
            )
        )

    else:

        await mensaje.edit(
            content=(
                "⚠️ El comando de inicio fue ejecutado, "
                "pero no se detectó la sesión screen."
            )
        )


# ============================================================
# ACTUALIZAR SERVIDOR
# ============================================================

class ConfirmarActualizacionView(discord.ui.View):

    def __init__(self, ctx):
        super().__init__(timeout=120)
        self.ctx = ctx

    @discord.ui.button(
        label="Apagar y actualizar",
        style=discord.ButtonStyle.danger,
        emoji="🛑"
    )
    async def apagar_actualizar(self, interaction, button):

        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "🚫 Solo la persona que inició la actualización puede usar estos botones.",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        self.stop()

        await iniciar_proceso_actualizacion(
            self.ctx,
            interaction.message
        )

    @discord.ui.button(
        label="Cancelar",
        style=discord.ButtonStyle.secondary,
        emoji="❌"
    )
    async def cancelar(self, interaction, button):

        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "🚫 Solo la persona que inició la actualización puede usar estos botones.",
                ephemeral=True
            )
            return

        await interaction.response.edit_message(
            content="❌ Actualización cancelada.",
            view=None
        )

        self.stop()


class IniciarDespuesActualizacionView(discord.ui.View):

    def __init__(self, ctx):
        super().__init__(timeout=120)
        self.ctx = ctx

    @discord.ui.button(
        label="Iniciar servidor",
        style=discord.ButtonStyle.success,
        emoji="🚀"
    )
    async def iniciar_servidor(self, interaction, button):

        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "🚫 Solo la persona que inició la actualización puede usar estos botones.",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        self.stop()

        await iniciar_servidor_despues_actualizacion(
            self.ctx,
            interaction.message
        )

    @discord.ui.button(
        label="No iniciar",
        style=discord.ButtonStyle.secondary,
        emoji="❌"
    )
    async def no_iniciar(self, interaction, button):

        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                "🚫 Solo la persona que inició la actualización puede usar estos botones.",
                ephemeral=True
            )
            return

        await interaction.response.edit_message(
            content="ℹ️ Actualización terminada. El servidor permanecerá apagado.",
            view=None
        )

        self.stop()


async def ejecutar_actualizacion():

    """
    Ejecuta UPDATE_COMMAND de config.json de forma asíncrona.
    Devuelve (True, salida) si SteamCMD termina correctamente.
    """

    if not UPDATE_COMMAND:
        return False, "UPDATE_COMMAND no está configurado."

    try:

        proceso = await asyncio.create_subprocess_shell(
            UPDATE_COMMAND,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

        salida = []

        while True:

            linea = await proceso.stdout.readline()

            if not linea:
                break

            texto = linea.decode(
                "utf-8",
                errors="replace"
            ).rstrip()

            if texto:
                salida.append(texto)
                print(f"[UPDATE] {texto}")

        codigo = await proceso.wait()

        return codigo == 0, "\n".join(salida[-20:])

    except Exception as error:

        print(
            f"❌ Error ejecutando actualización: {error}"
        )

        return False, str(error)


async def mostrar_pregunta_iniciar(
    ctx,
    mensaje
):

    await mensaje.edit(
        content=(
            "✅ **Actualización completada correctamente.**\n\n"
            "Project Zomboid ya fue actualizado.\n"
            "¿Deseas iniciar nuevamente el servidor?"
        ),
        view=IniciarDespuesActualizacionView(ctx)
    )


async def iniciar_servidor_despues_actualizacion(
    ctx,
    mensaje
):

    global actualizacion_en_curso

    await mensaje.edit(
        content="🚀 Iniciando nuevamente Project Zomboid...",
        view=None
    )

    resultado = ejecutar_comando(
        START_COMMAND
    )

    if not resultado:

        actualizacion_en_curso = False

        await mensaje.edit(
            content="❌ Error ejecutando el comando de inicio."
        )

        return

    iniciado = await esperar_servidor_arranque(
        90
    )

    actualizacion_en_curso = False

    if iniciado:

        await mensaje.edit(
            content="✅ Servidor actualizado e iniciado correctamente."
        )

    else:

        await mensaje.edit(
            content=(
                "⚠️ El comando de inicio fue ejecutado, "
                "pero no se detectó la sesión screen."
            )
        )


async def iniciar_proceso_actualizacion(
    ctx,
    mensaje
):

    global actualizacion_en_curso

    try:

        # --------------------------------------------------------
        # SI ESTABA ENCENDIDO, APAGARLO PRIMERO
        # --------------------------------------------------------

        if servidor_encendido():

            await mensaje.edit(
                content=(
                    "🛑 Enviando `quit` al servidor para guardar "
                    "la partida antes de actualizar..."
                ),
                view=None
            )

            resultado_apagado = ejecutar_comando(
                STOP_COMMAND
            )

            if not resultado_apagado:

                actualizacion_en_curso = False

                await mensaje.edit(
                    content=(
                        "❌ No se pudo enviar el comando `quit` "
                        "al servidor. La actualización fue cancelada."
                    )
                )

                return

            await mensaje.edit(
                content=(
                    "💾 Guardando partida y esperando a que "
                    "Project Zomboid termine de apagarse..."
                ),
                view=None
            )

            apagado = await esperar_servidor_apagado(
                120
            )

            if not apagado:

                actualizacion_en_curso = False

                await mensaje.edit(
                    content=(
                        "❌ El servidor no terminó de apagarse "
                        "dentro del tiempo esperado.\n"
                        "La actualización fue cancelada."
                    )
                )

                return

        # --------------------------------------------------------
        # ACTUALIZAR
        # --------------------------------------------------------

        await asyncio.sleep(3)

        await mensaje.edit(
            content=(
                "🔄 **Actualizando Project Zomboid...**\n\n"
                "⏳ SteamCMD está descargando/verificando los archivos.\n"
                "Esto puede tardar varios minutos."
            ),
            view=None
        )

        actualizado, salida = await ejecutar_actualizacion()

        if not actualizado:

            actualizacion_en_curso = False

            await mensaje.edit(
                content=(
                    "❌ **La actualización falló.**\n\n"
                    "SteamCMD devolvió un error.\n"
                    "El servidor permanecerá apagado.\n\n"
                    "Revisa la consola del bot para ver el detalle."
                ),
                view=None
            )

            return

        # --------------------------------------------------------
        # ACTUALIZACION TERMINADA
        # --------------------------------------------------------

        await mostrar_pregunta_iniciar(
            ctx,
            mensaje
        )

    except Exception as error:

        actualizacion_en_curso = False

        print(
            f"❌ Error durante actualización: {error}"
        )

        await mensaje.edit(
            content=(
                "❌ Ocurrió un error durante la actualización.\n"
                "El servidor permanecerá apagado."
            ),
            view=None
        )


@bot.command(
    name="actualizar"
)
async def actualizar(ctx):

    global actualizacion_en_curso

    if not es_admin(ctx):

        await ctx.send(
            "🚫 No tienes permisos para actualizar el servidor."
        )

        return

    # ------------------------------------------------------------
    # EVITAR DOS ACTUALIZACIONES AL MISMO TIEMPO
    # ------------------------------------------------------------

    if actualizacion_en_curso:

        await ctx.send(
            "⚠️ Ya hay una actualización del servidor en curso."
        )

        return

    async with actualizacion_lock:

        if actualizacion_en_curso:

            await ctx.send(
                "⚠️ Ya hay una actualización del servidor en curso."
            )

            return

        actualizacion_en_curso = True

        # --------------------------------------------------------
        # SI EL SERVIDOR ESTÁ ENCENDIDO
        # --------------------------------------------------------

        if servidor_encendido():

            mensaje = await ctx.send(
                (
                    "🔄 **Actualizar servidor**\n\n"
                    "🟢 El servidor está actualmente encendido.\n"
                    "Para actualizar Project Zomboid es necesario "
                    "apagarlo primero.\n\n"
                    "¿Deseas apagar el servidor y continuar "
                    "con la actualización?"
                ),
                view=ConfirmarActualizacionView(ctx)
            )

            # La tarea continuará desde el botón.
            # No liberamos el estado hasta que termine la operación.
            return

        # --------------------------------------------------------
        # SI YA ESTÁ APAGADO
        # --------------------------------------------------------

        mensaje = await ctx.send(
            (
                "🔄 **Actualización de Project Zomboid**\n\n"
                "🔴 El servidor ya está apagado.\n"
                "Iniciando actualización..."
            )
        )

        await iniciar_proceso_actualizacion(
            ctx,
            mensaje
        )


# ============================================================
# ACTUALIZAR ESTADO DE DISCORD
# ============================================================

@tasks.loop(
    seconds=STATUS_UPDATE_SECONDS
)
async def actualizar_estado():

    global ultimo_estado


    try:

        # ----------------------------------------------------
        # PRIMERO: comprobar servidor
        # ----------------------------------------------------

        if not servidor_encendido():

            texto = "🔴 Servidor apagado | PZ"

            ultimo_estado = "OFFLINE"


        else:

            # ------------------------------------------------
            # SERVIDOR ENCENDIDO
            # ------------------------------------------------

            jugadores = obtener_jugadores()

            cantidad = len(jugadores)


            texto = (
                f"🟢 {cantidad} jugadores | PZ Online"
            )

            ultimo_estado = "ONLINE"


        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(
                name=texto
            )
        )


    except Exception as error:

        print(
            f"❌ Error actualizando estado Discord: {error}"
        )


# ============================================================
# ERRORES DE COMANDOS
# ============================================================

@bot.event
async def on_command_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.CommandNotFound
    ):

        await ctx.send(
            f"❌ Comando no encontrado.\n"
            f"Usa `{PREFIX}help`"
        )

        return


    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):

        await ctx.send(
            "⚠️ Falta un argumento."
        )

        return


    print(
        f"❌ Error comando: {error}"
    )


# ============================================================
# MENSAJES
# ============================================================

@bot.event
async def on_message(
    message
):

    if message.author == bot.user:

        return


    await bot.process_commands(
        message
    )


# ============================================================
# DESCONEXION
# ============================================================

@bot.event
async def on_disconnect():

    print(
        "⚠️ Bot desconectado de Discord"
    )


# ============================================================
# INICIO DEL BOT
# ============================================================

if __name__ == "__main__":

    try:

        bot.run(
            TOKEN
        )

    except Exception as error:

        print(
            f"❌ Error iniciando bot: {error}"
        )
