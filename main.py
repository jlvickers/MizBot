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
domains = ['@umsystem.edu','@missouri.edu','@mail.missouri.edu']
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
    print("logged in as \n{} \n{}".format(bot.user.name, bot.user.id))
    print("------")

# executes function when reaction is added to the message which message_id specifies. In the use case, this was a message with instructions on how the verification bot works.
@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    p1 = None
    if message_id != 747177247403671705:
        return
    
    # checks payload name for correct emoji reactions and executes accordingly
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

# checks if the channel it's evoked in is a direct message channel, checks if the email provided is a valid MU domain. If so, sends an email and provides instructions accordingly.
@bot.command()
async def email(ctx, email):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        if any(x in email for x in domains):
            for idx, val in enumerate(userlist):
                if ctx.author.id == val.id:
                    code = val.code
                    userlist[idx].email = email
            email = email
            content = 'Your verification code is {0}. Reply to the discord bot in DMs with \'v!verify {0}\''.format(str(code))
            ezgmail.send(email,subject,content)
            await ctx.author.send("Thanks! Check your email for a code. If you can't find it, make sure to check your spam folder.\n Once you have your code, reply to the bot with v!verify <your code>")
            await ctx.author.send("[NOTICE] The University of Missouri's IT department will flag the email as potential phishing attack. This is not the case, and you will NEVER have to click on links or download attachments from Mizzou Esports this way.")
        else:
            await ctx.author.send("Sorry, that's not a Mizzou email.")

#checks if the channel is a direct message channel, then executes logic accordingly.
@bot.command()
async def verify(ctx, code):
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
        if str(code) == str(vernumb):
            disc = discord.utils.find(lambda g : g.id == guild, bot.guilds)
            if MizRole == 'Student': 
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

#Logging function to view all members verified from a text file. Only executable in the channel specified, which in this case was an admin only channel
@bot.command()
async def ReadLog(ctx):
    if ctx.channel.id == 743295692407046195:
        logging = open('VerifiedUsers.txt', 'r')
        await ctx.channel.send(logging.read())
        logging.close()

bot.run(token)

# Looking back there is a lot of duplicate code I could've avoided and tightened up some logic, but for only having about 2-3 days to figure out a verification solution and learn
# these libraries I think the outcome is good. To expand on this project idea, I would most likely hold logging information in a MySQL database where it could be parsed easier
# and hold more information that could be useful. I would also use a different automated email solution that could be ran through a university domain rather than a gmail account.