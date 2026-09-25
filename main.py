import discord
from discord.ext import commands
from control_panel_view import ControlPanelView
import asyncio

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.add_view(ControlPanelView())
    await bot.tree.sync()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"An error occurred: {error}")

@bot.tree.command(name="setup", description="Set up the Butterfly VC channels.")
async def setup(interaction: discord.Interaction):
    # Defer the response to prevent the interaction from timing out.
    await interaction.response.defer(ephemeral=True)

    # Create the Butterfly VC category and the generator voice channel.
    guild = interaction.guild
    category = await guild.create_category("Butterfly VC")
    await guild.create_voice_channel("𝗕𝘂𝘁𝘁𝗲𝗿𝗳𝗹𝘆 VC", category=category)
    await interaction.followup.send("Butterfly VC has been set up!")


@bot.event
async def on_voice_state_update(member, before, after):
    try:
        # Check if the user joined the generator channel.
        if after.channel and after.channel.name == "𝗕𝘂𝘁𝘁𝗲𝗿𝗳𝗹𝘆 VC":
            guild = member.guild
            category = after.channel.category
            channel_name = f"🔊 {member.display_name}'s VC"

            # Create overwrites to make the channel private.
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, connect=False, view_channel=False),
                member: discord.PermissionOverwrite(read_messages=True, connect=True, view_channel=True)
            }

            # Create the text and voice channels.
            text_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)
            new_channel = await guild.create_voice_channel(name=channel_name, category=category, overwrites=overwrites)

            # Move the user to their new channel.
            await member.move_to(new_channel)

            # Create a role for the user.
            role = await guild.create_role(name=channel_name)
            await member.add_roles(role)

            # Send the control panel.
            if member.voice and member.voice.channel == new_channel:
                embed = discord.Embed(title="Butterfly VC Control Panel", description="Use the buttons below to manage your channel.")
                embed.add_field(name="🚫 Ban", value="Ban a user from your channel.", inline=True)
                embed.add_field(name="🎚️ Bitrate", value="Set the bitrate of your channel.", inline=True)
                embed.add_field(name="🙈 Hide", value="Toggle the visibility of your channel.", inline=True)
                embed.add_field(name="➕ Invite", value="Invite a user to your channel.", inline=True)
                embed.add_field(name="👥 Limit", value="Set the user limit of your channel.", inline=True)
                embed.add_field(name="🔒 Lock", value="Toggle the lock on your channel.", inline=True)
                embed.add_field(name="📝 Name", value="Set the name of your channel.", inline=True)
                embed.add_field(name="🔄 Transfer", value="Transfer ownership of your channel.", inline=True)
                await text_channel.send(embed=embed, view=ControlPanelView())

        # Check if the user left a temporary channel and if the channel is now empty.
        if before.channel and before.channel.name.endswith("'s VC"):
            # Add a small delay to allow the members list to update.
            await asyncio.sleep(1)
            if before.channel and not before.channel.members:
                guild = member.guild

                # Delete the role.
                role = discord.utils.get(guild.roles, name=before.channel.name)
                if role:
                    await role.delete()

                # Delete the text channel.
                text_channel = discord.utils.get(guild.text_channels, name=before.channel.name)
                if text_channel:
                    try:
                        await text_channel.delete()
                    except discord.errors.NotFound:
                        pass

                # Delete the voice channel.
                try:
                    await before.channel.delete()
                except discord.errors.NotFound:
                    pass
    except Exception as e:
        print(f"An error occurred in on_voice_state_update: {e}")

bot.run("MTU1Mjg3MDE2MjY0MDgwMTg4Mw.GCeZsB.kdrb6aHE5PcDCU8a8cKPOTpcqgyKRg2WsQ9QQ4")
