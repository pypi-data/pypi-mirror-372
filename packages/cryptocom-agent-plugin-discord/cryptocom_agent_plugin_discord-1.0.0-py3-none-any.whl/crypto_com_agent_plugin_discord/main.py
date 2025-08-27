import logging
import discord
from discord.ext import commands
from crypto_com_agent_client.plugins.base import AgentPlugin

logger = logging.getLogger(__name__)


class DiscordPlugin(AgentPlugin):
    mode = "primary"

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.bot = None
        self.handler = None

    def setup(self, handler):
        logger.info("[DiscordPlugin] Setting up...")
        self.handler = handler

        intents = discord.Intents.default()
        intents.message_content = True

        self.bot = commands.Bot(command_prefix="!", intents=intents)

        @self.bot.event
        async def on_ready():
            logger.info(f"Discord bot ready as {self.bot.user}")

        @self.bot.command(name="start")
        async def start(ctx):
            try:
                await ctx.send(
                    "Hello! I am your Crypto.com AI Agent. Send me a message to interact!"
                )
            except Exception as e:
                logger.error(f"[DiscordPlugin/start] Error: {e}")
                await ctx.send("An error occurred. Please try again.")

        @self.bot.event
        async def on_message(message):
            if message.author == self.bot.user:
                return

            try:
                user_message = message.content
                chat_id = message.channel.id
                response = self.handler.interact(user_message, thread_id=chat_id)

                MAX_LENGTH = 2000
                if len(response) > MAX_LENGTH:
                    for i in range(0, len(response), MAX_LENGTH):
                        await message.channel.send(response[i : i + MAX_LENGTH])
                else:
                    await message.channel.send(response)

            except Exception as e:
                logger.error(f"[DiscordPlugin/on_message] Error: {e}")
                await message.channel.send(
                    "An error occurred while processing your request."
                )

            await self.bot.process_commands(message)

        logger.info("[DiscordPlugin] Setup complete.")

    def run(self):
        logger.info("[DiscordPlugin] Starting bot...")
        try:
            self.bot.run(self.bot_token)
        except Exception as e:
            logger.error(f"[DiscordPlugin/run] Error: {e}")
        finally:
            logger.info("[DiscordPlugin] Shutdown complete")
