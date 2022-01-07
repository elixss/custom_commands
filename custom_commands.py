import sqlite3
import disnake
from disnake import Embed
from disnake.ext import commands

prefix = "!"

colour = 0x5865f2


class CustomCommands(commands.Cog, name="Custom commands"):
    def __init__(self, bot):
        """Early testing for custom commands."""
        self.bot = bot

    @commands.group(name="command", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def command(self, ctx):
        """Create custom guild commands!"""

        e = Embed(title="Custom commands",
                  description="You can now test out custom commands!\n"
                              "Usage: `command <subcommand>`\n"
                              "Every server can have a total of 5 custom commands.", color=colour)
        e.add_field(name="Here are the commands.",
                    value=f"`{prefix}add <name> <content>` - Add a command\n"
                          f"`{prefix}remove <name>` - Remove a command\n"
                          f"`{prefix}list` - Shows the servers custom commands\n", inline=False)
        e.add_field(name="Keywords",
                    value="`{guild}` - The name of your server.\n"
                          "`{members}` - The amount of members in your server.\n"
                          "`{bot}` - The amount of bots in your server.\n"
                          "`{member}` - The amount of members in your server.", inline=False)
        await ctx.reply(embed=e, mention_author=False)
        return

    @command.command(name="add")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def add_command(self, ctx, command: str, *, content: str):
        """Add a custom command."""
        db = sqlite3.connect("custom_commands.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT cmd_name FROM main WHERE guild_id LIKE '{ctx.guild.id}%'")
        cmd = cursor.fetchall()

        cursor.execute(f"SELECT guild_id, COUNT(*) FROM main GROUP BY guild_id HAVING COUNT(*) > 1;")

        guilds = cursor.execute("SELECT guild_id FROM main")
        print(guilds)

        result = guilds.fetchall()
        print(result)
        for i in range(len(cmd)):
            if i >= 4:
                return await ctx.send("Limit for custom commands is **5**.")
        if f"{ctx.guild.id}-0" not in str(result):
            guild = f"{ctx.guild.id}-0"
        if f"{ctx.guild.id}-0" in str(result):
            guild = f"{ctx.guild.id}-1"
        if f"{ctx.guild.id}-1" in str(result):
            guild = f"{ctx.guild.id}-2"
        if f"{ctx.guild.id}-2" in str(result):
            guild = f"{ctx.guild.id}-3"
        if f"{ctx.guild.id}-3" in str(result):
            guild = f"{ctx.guild.id}-4"

        sql1 = (f"INSERT INTO main(guild_id, cmd_name, cmd_content) VALUES(?, ?, ?)")
        val1 = (guild, command.lower(), content)
        cursor.execute(sql1, val1)
        db.commit()
        cursor.close()
        db.close()
        e = Embed(title="", description="", colour=colour)
        e.add_field(name="A new custom command has been created!", value=f"Try it out: `{prefix}{command}`")
        await ctx.reply(embed=e, mention_author=False)

    @command.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def remove_command(self, ctx, command: str):
        class View(disnake.ui.View):
            def __init__(self):
                super().__init__()

            @disnake.ui.button(label="Yes, delete it",
                               emoji=disnake.PartialEmoji(name="yes", id=890631200476114964, animated=True))
            async def yesRemoveCommand(self, button, interaction):
                cursor.execute(
                    f"DELETE FROM main WHERE cmd_name = '{command}' AND guild_id LIKE '{ctx.guild.id}%'")
                db.commit()
                cursor.close()
                db.close()
                await interaction.response.edit_message(
                    f"Command `{command}` has been deleted by {ctx.author.mention}.", view=None)
                self.stop()

            @disnake.ui.button(label="No, don't delete it",
                               emoji=disnake.PartialEmoji(name="no", id=890631116254490745, animated=True))
            async def noDontRemoveCommand(self, button, interaction):
                await interaction.response.edit_message("Request cancelled.", view=None)
                cursor.close()
                db.close()
                self.stop()

        db = sqlite3.connect("custom_commands.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT cmd_name FROM main WHERE guild_id LIKE '{ctx.guild.id}%'")
        result = cursor.fetchone()
        if result is None:
            return await ctx.reply("You either don't have custom commands, or your command doesn't exist.")
        else:
            if str(command) in str(result[0]):
                await ctx.reply(
                    f"You are trying to delete the following custom command: `{command}`. Are you sure?",
                    view=View())

    @command.command(name="list")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def command_list(self, ctx):
        db = sqlite3.connect("custom_commands.sqlite")
        cursor = db.cursor()
        cursor.execute(
            f"SELECT cmd_name FROM main WHERE guild_id LIKE '{ctx.guild.id}%'"
        )
        result = cursor.fetchall()

        if result is None:
            return await ctx.reply("You don't have custom commands.")

        if result is not None:
            try:

                cmd = ""
                for command in result:
                    cmd += "`" + "`, `".join(command) + "`, "
                cmd = cmd[:-2]
                e = Embed(title="Your servers custom commands",
                          description='Here are the custom commands for this server.\n')
                e.add_field(name=f"Your server has **{len(result)}** custom command(s).",
                            value=cmd)
                await ctx.reply(embed=e, mention_author=False)
            except disnake.HTTPException:
                return await ctx.reply("You don't have custom commands or I can't display them.")

    @commands.Cog.listener()
    async def on_message(self, message):
        db = sqlite3.connect("custom_commands.sqlite")
        cursor = db.cursor()
        guild = message.guild
        members = len(message.guild.members)
        bot = len(list(filter(lambda m: m.bot, message.guild.members)))
        human = len(list(filter(lambda m: not m.bot, message.guild.members)))

        cursor.execute(
            f"SELECT cmd_name FROM main WHERE guild_id LIKE '{message.guild.id}%'")
        cmd_name = cursor.fetchall()
        cursor.execute(
            f"SELECT cmd_content FROM main WHERE guild_id LIKE '{message.guild.id}%'")
        cmd_content = cursor.fetchall()
        for i in range(len(cmd_name)):
            if message.content.lower() == f"{prefix}" + "".join(
                    cmd_name[i]).lower() or message.content.lower() == self.bot.user.mention + " " + "".join(
                cmd_name[i]).lower():
                await message.channel.trigger_typing()
                await message.reply("".join(cmd_content[i]).format(members=members, guild=guild, bot=bot, human=human),
                                    mention_author=False)


def setup(bot):
    bot.add_cog(CustomCommands(bot))
