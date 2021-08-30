import ezgmail
import os
import struct
import json
import discord
from discord.ext import commands
import discord.utils
# Mizzou Esports student verification bot created by Jackson Vickers. The main function is to take user information
# when they react to a specific message in a channel, create a DM conversation with them. From there, they provide
# the bot with their email address that matches the University of Missouri - Columbia's domains and the bot sends
# an email containing a random verification code using the ezgmail library. Once the user successfully verifies their
# student email, their information is added to a logging file for easy moderation if necessary.
class UserData:
    def __init__(self, memberID, email, code, id, guild, role):
        self.email = email
        self.code = code
        self.id = id
        self.memberid = memberID
        self.guild = guild
        self.role = role
    def getID(self):
        return self.id
    def getCode(self):
        return self.code
    def getEmail(self):
        return self.email
    def getMember(self):
        return self.memberid
    def getGuild(self):
        return self.guild
    def getRole(self):
        return self.role


bot = commands.Bot(command_prefix='v!')
domain = '@umsystem.edu'
domain2 = '@missouri.edu'
domain3 = '@mail.missouri.edu'
subject = 'Mizzou Esports Discord Verification'
userlist = []
try:
    config = json.loads(open('config.json').read())
    token = config['bot_token']
    server_id = config['server_id']
    role_name = config['role_name']
except:
    print("FATAL ERROR: Couldn't read config")

@bot.event
async def on_ready():
    print("logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    p1 = None
    print(payload.emoji)
    if not message_id == 747177247403671705:
        return
    if payload.emoji.name == 'Tiger':
        email = ""
        vernum = struct.unpack('H', os.urandom(2))
        if payload.emoji.name == 'Tiger':
            p1 = UserData(payload.member, email, vernum[0], payload.member.id, payload.guild_id, 'Student')
            userlist.append(p1)
        await payload.member.send("Reply in this DM thread with your UM Systems email address using v!email <email address>")
        await payload.member.send("If you have issues obtaining a role, check out #verification-questions or DM Skiritai#1478.")

    if payload.emoji.name == 'mortarboard':
        email = ""
        vernum = struct.unpack('H', os.urandom(2))
        if payload.emoji.name == 'mortarboard':
            p1 = UserData(payload.member, email, vernum[0], payload.member.id, payload.guild_id, 'Alumni')
            userlist.append(p1)
        await payload.member.send("Reply in this DM thread with your UM Systems email address using v!email <email address>")
        await payload.member.send("If you have issues obtaining a role, check out #verification-questions or DM Skiritai#1478.")
@bot.command()
async def email(ctx, arg):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        if domain in arg or domain2 in arg or domain3 in arg:
            for idx, val in enumerate(userlist):
                if ctx.author.id == val.id:
                    index = idx
                    code = val.code
                    id = val.id
                    userlist[idx].email = arg
            email = arg
            content = 'Your verification code is {0}. Reply to the discord bot in DMs with \'v!verify {0}\''.format(str(code))
            ezgmail.send(email,subject,content)
            await ctx.author.send("Thanks! Check your email for a code. If you can't find it, make sure to check your spam folder.\n Once you have your code, reply to the bot with v!verify <your code>")
            await ctx.author.send("[NOTICE] The University of Missouri's IT department will flag the email as potential phishing attack. This is not the case, and you will NEVER have to click on links or download attachments from Mizzou Esports this way.")
        else:
            await ctx.author.send("Sorry, that's not a Mizzou email.")
            return

@bot.command()
async def verify(ctx, arg):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        logging = open("VerifiedUsers.txt","a")
        vernumb = ''
        member = ''
        email = ''
        role = ''
        guild = None
        for idx, val in enumerate(userlist):
            if ctx.author.id == val.id:
                vernumb = val.getCode()
                member = val.getMember()
                guild = val.getGuild()
                email = val.getEmail()
                MizRole = val.getRole()
        if str(arg) == str(vernumb):
            disc = discord.utils.find(lambda g : g.id == guild, bot.guilds)
            server = bot.get_guild(server_id)
            if MizRole == 'Student':
                alumRole = discord.utils.get(disc.roles, name = 'Mizzou Alum')   
                role = discord.utils.get(disc.roles, name = 'Mizzou Student')
                removeRole = discord.utils.get(disc.roles, name = 'Unverified Mizzou Student')
                await member.add_roles(role, atomic = True)
                await member.remove_roles(removeRole, atomic = True)
            elif MizRole == 'Alumni':
                role = discord.utils.get(disc.roles, name = 'Mizzou Alum')
                removeRole = discord.utils.get(disc.roles, name = 'Unverified Alumni')
                await member.add_roles(role, atomic = True)
                await member.remove_roles(removeRole, atomic = True)
            await ctx.author.send("Thank you, enjoy the discord!")
            logging.write(str(ctx.author)+" "+str(ctx.author.id)+" "+str(email)+ " "+ str(role)+"\n")
            logging.close()
        else:
            await ctx.author.send("Sorry, that's the wrong verification number")

@bot.command()
async def ReadLog(ctx):
    if ctx.channel.id == 743295692407046195:
        logging = open('VerifiedUsers.txt', 'r')
        await ctx.channel.send(logging.read())
        logging.close()

bot.run(token)