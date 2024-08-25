import os
import dotenv

from nextcord import Interaction, TextChannel, Permissions, Message, Intents
from nextcord.ext import commands

dotenv.load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not DISCORD_BOT_TOKEN:
    print('DISCORD_BOT_TOKEN environment variable not defined.')
    exit(1)

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents)

# This is temporary
counting_channel: TextChannel  | None = None
expected_number = 1
prev_id = None
curr_id = None

@bot.slash_command(description='Sets the counting channel', default_member_permissions=Permissions(administrator=True))
async def count_in(interaction: Interaction, channel: TextChannel):
    global counting_channel
    counting_channel = channel
    await interaction.response.send_message(f"{counting_channel.mention} is now the counting channel!", ephemeral=True)

@bot.event
async def on_message(message: Message):
    print(f'Message: {message.content}')

    global counting_channel
    global expected_number
    global prev_id
    global curr_id

    if counting_channel is None:
        return

    if message.channel.id != counting_channel.id:
        return
    
    if message.content.isdigit():
        value = int(message.content)

        prev_id = curr_id
        curr_id = message.author.id

        if prev_id is not None and curr_id is not None:
            if prev_id == curr_id:
                await message.add_reaction(emoji='❌')
                await counting_channel.send(f"{message.author.mention} ruined it at {expected_number}! You can't count two numbers in a row.")
                expected_number = 1
                prev_id = None
                curr_id = None
                return

        if value == expected_number:
            await message.add_reaction(emoji='✅')
            expected_number += 1
            return
        else:
            await message.add_reaction(emoji='❌')
            expected_number = 1
            prev_id = None
            curr_id = None
            await counting_channel.send(f"{message.author.mention} ruined it at {expected_number - 1}! The next number is 1")
            return

bot.run(DISCORD_BOT_TOKEN)