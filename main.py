import discord
from discord.ext import commands
import google.generativeai as genai

# 1. إعداد الذكاء الاصطناعي (Gemini API)
genai.configure(api_key='حط_مفتاح_API_مال_Gemini_هنا')
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# 2. إعدادات صلاحيات ديسكورد
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# --- نظام التذاكر (Tickets System) ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التذكرة 🔒", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("جاري إغلاق التذكرة خلال 3 ثوانٍ...")
        import asyncio
        await asyncio.sleep(3)
        await interaction.channel.delete()

class TicketLaunchView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="فتح تذكرة 🎫", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        channel_name = f"ticket-{user.name}"

        existing = discord.utils.get(guild.channels, name=channel_name)
        if existing:
            await interaction.response.send_message(f"عندك تذكرة مفتوحة بالفعل: {existing.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        embed = discord.Embed(
            title="تذكرة دعم جديدة 🎫",
            description=f"أهلاً {user.mention}، تفضل باختصار مشكلتك وسيرد عليك طاقم الإدارة قريباً.",
            color=discord.Color.blue()
        )
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"تم فتح التذكرة: {channel.mention}", ephemeral=True)

# --- أحداث البوت (Events) ---
@bot.event
async def on_ready():
    print(f'البوت شغال وبخدمتك باسم: {bot.user}')

# الذكاء الاصطناعي للرد على الرسائل والتاق
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # إذا الشخص سوى تاق للبوت أو حكة بالروم
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            try:
                # تنظيف النص من التاق
                prompt = message.content.replace(f'<@{bot.user.id}>', '').strip()
                if not prompt:
                    prompt = "مرحبا"
                
                response = ai_model.generate_content(prompt)
                await message.reply(response.text)
            except Exception as e:
                await message.reply("عذراً، حدث خطأ أثناء الاتصال بالذكاء الاصطناعي.")

    await bot.process_commands(message)

# --- أوامر الإدارة (Moderation Commands) ---

# أمر إعداد التذاكر
@bot.command(name='setup_tickets')
@commands.has_permissions(administrator=True)
async def setup_tickets(ctx):
    embed = discord.Embed(
        title="قسم الدعم الفني 🎫",
        description="اضغط على الزر أدناه لفتح تذكرة خاصة والتواصل مع الإدارة.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=TicketLaunchView())

# مسح الرسائل
@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'تم مسح {amount} رسالة بنجاح!', delete_after=3)

# طرد عضو
@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="بدون سبب"):
    await member.kick(reason=reason)
    await ctx.send(f'تم طرد {member.mention} | السبب: {reason}')

# حظر عضو
@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="بدون سبب"):
    await member.ban(reason=reason)
    await ctx.send(f'تم حظر {member.mention} | السبب: {reason}')

# كتم عضو (Mute)
@bot.command(name='mute')
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False)
    await member.add_roles(muted_role)
    await ctx.send(f'تم كتم {member.mention} بنجاح.')

# إلغاء الكتم (Unmute)
@bot.command(name='unmute')
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f'تم فك الكتم عن {member.mention}.')

# تشغيل البوت
bot.run('MTU2MzU2ODk5ODA0MDM0NjcxNQ.GY3GzU.y99mIcy5_lWFA9w7MyRbNfjDPtd8Xu_Qe_kp3M')
