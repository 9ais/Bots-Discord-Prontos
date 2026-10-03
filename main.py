import discord
from discord import app_commands
from discord.ui import *
from discord.ext import commands
from configBot import *
import sqlite3

token = tokenBot
prefix = prefixBot

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.event
async def on_ready():
    BotName = bot.user.name
    print(f'{BotName} está Online!')
    
    sinc = await bot.tree.sync()
    print(f'Foram Sincronizados {len(sinc)} Comandos Slash')
    
    await connectData()


@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    
    try:
        if message.channel.id != channelAntiRaid.id:
            return
        
    except NameError:  
        channelAntiRaid = bot.get_channel((checkChannel(message.guild.id)))
        if message.channel.id != channelAntiRaid.id:
                    return
        
    from datetime import datetime, timedelta, timezone

    userSuspect = message.author
    limite = datetime.now(timezone.utc) - timedelta(minutes=5)

    for channel in message.guild.text_channels:
        try:
            mensagens = []

            async for msg in channel.history(after=limite):
                if msg.author.id == userSuspect.id:
                    mensagens.append(msg)

            if mensagens:
                await channel.delete_messages(mensagens)

        except Exception as e:
            print(f"Erro no canal {channel.name}: {e}")
            
    
    punish = checkPunish(message.guild.id)
            
    if punish == 0:
        await userSuspect.ban(reason='Sistema de AntiRaid 9Shield')
    elif punish == 1:
        await userSuspect.kick(reason='Sistema de AntiRaid9Shield')
    elif punish == 2:
        await userSuspect.timeout()
            


@bot.tree.command(name="config", description="Configurar um canal")
@app_commands.describe(canal="Selecione o canal")
@app_commands.checks.has_permissions(administrator=True)
async def config(interaction: discord.Interaction, canal: discord.TextChannel):
    checkServer(interaction.guild.id)
    updateChannel(interaction.guild.id, canal.id)
    updateActive(interaction.guild.id)
    
    user = interaction.user
    defaultEmbed = discord.Embed(color=defaultColor)
    botUser = interaction.guild.me 
    
    punish = checkPunish(interaction.guild.id)
    
    if botUser.guild_permissions.administrator and user.guild_permissions.administrator:
        defaultEmbed.title = "🔒 Canal Restrito — Monitoramento Ativo"
        defaultEmbed.set_footer(text=f'Sistema Anti-Selfbot • {bot.user.name}')
        defaultEmbed.description = f"""Canal de monitoramento configurado com sucesso.

O sistema passará a monitorar automaticamente este canal e identificar mensagens enviadas por bots ou selfbots não autorizados.

> Monitoramento: Ativo
> Canal: <#{canal.id}>

As mensagens detectadas serão tratadas de acordo com as regras definidas pela administração.
"""


        await interaction.response.send_message(embed=defaultEmbed, ephemeral=True)
        defaultEmbed.title = '🚫 Canal Restrito — Não envie mensagens aqui'
        defaultEmbed.description = """
Este canal é **monitorado automaticamente**.

Qualquer mensagem enviada aqui será tratada como atividade de selfbot / automação não autorizada e resultará em:

> 🧹 Remoção de todas as suas mensagens dos últimos 5 minutos
""" 
        if punish == 0:
            defaultEmbed.description += "> ⚠️ Atenção: O envio de mensagens neste canal está sujeito à **Banimento automático**."
        elif punish == 1:
            defaultEmbed.description += "> ⚠️ Atenção: O envio de mensagens neste canal está sujeito à **Expulsão automática**."
        elif punish == 2:
            defaultEmbed.description += "> ⚠️ Atenção: O envio de mensagens neste canal está sujeito à **Mute automático**."
            
        defaultEmbed.description += "\nNão interaja com este canal.\n"
        
        await canal.send(embed=defaultEmbed)
        
    else:
        await interaction.response.send_message(f"Voce não tem permissao para executar esse comando!", ephemeral=True)
    
 
 
@bot.tree.command(name='antiraid', description='Ativa ou desativa o sistema Anti-Raid do servidor.')
@app_commands.checks.has_permissions(administrator=True)
async def antiraid(interaction: discord.Integration):
    checkServer(interaction.guild.id)
    system = checkActive(interaction.guild.id)
    type = checkPunish(interaction.guild.id)
    
    embedFodase = discord.Embed(title='🛡️ Sistema de Monitoramento', color=defaultColor)
    embedFodase.description = "Proteção automática ativa neste servidor.\n\n"
    if system:
        global channelAntiRaid
        channelAntiRaid = interaction.guild.get_channel(checkChannel(interaction.guild.id))
        embedFodase.description += """🟢 **Status**: Online
        🛡️ **Monitoramento**: Ativado"""
    else:
        embedFodase.description += """🔴 **Status**: Offline
        🛡️ **Monitoramento**: Desativado"""
        
    
    if type == 0:
        embedFodase.description += "\n⚙️ **Modo de Punição**: Banimento"
    elif type == 1: 
        embedFodase.description += "\n⚙️ **Modo de Punição**: Expulsão"
    elif type == 2: 
        embedFodase.description += "\n⚙️ **Modo de Punição**: Aviso"
        
    if system != 0:
        embedFodase.description += f"\n>O sistema está monitorando o Chat Configurado configurado (<#{channelAntiRaid.id}>) e poderá aplicar as ações definidas pela administração." 
        
    view = View()
    labelText = 'Ativar' if not system else 'Desativar'
    buttonStyle = discord.ButtonStyle.success if not system else discord.ButtonStyle.danger 
    buttonEnableAndDisable = Button(label=labelText, style=buttonStyle)
    
    async def callback_button(interaction: discord.Interaction):

        if system:
            messageText = 'Sistema Desativado!'
        else: 
            if not checkChannel(interaction.guild.id):
                await interaction.response.send_message('Você precisa configurar um Canal primeiro, use /config', ephemeral=True)
                return
            
            messageText = 'Sistema Ativado!'
            
        updateActive(interaction.guild.id)
        system = not system
        await interaction.response.send_message(messageText, ephemeral=True)
    
    buttonEnableAndDisable.callback = callback_button
    view.add_item(buttonEnableAndDisable)
               
    await interaction.response.send_message(embed=embedFodase, ephemeral=True, view=view)
    
    
@bot.tree.command(name='setpunish', description='Configuração de Punição')
@app_commands.checks.has_permissions(administrator=True)
async def setpunish(interaction: discord.Interaction):
    selectMenu = discord.ui.Select(
        placeholder='Escolha uma Punição...',
        options=[
            discord.SelectOption(label='Banimento', value='punishBan'),
            discord.SelectOption(label='Expulsão (Recomendado)', value='punishKick'),
            discord.SelectOption(label='Apenas Aviso', value='punishWarn')
        ]
    )
    
    async def selectMenu_callback(interaction: discord.Interaction):
        punishType = selectMenu.values[0]
        typeName = ''
        serverId = interaction.guild.id
        
        if punishType == 'punishBan':
            updatePunish(serverId, 0)
            typeName = 'Banimento automatico'
            
        if punishType == 'punishKick':
            updatePunish(serverId, 1)
            typeName = 'Expulsão automatica'
            
        if punishType == 'punishWarn':
            updatePunish(serverId, 2)
            typeName = 'Aviso'
            
        await interaction.response.send_message(f'Você selecionou a Punição **{typeName}**, todos os Supostos SelfBots serão Punidos com essa Opção')
        
    view = View()
    selectMenu.callback = selectMenu_callback
    
    view.add_item(selectMenu)
    
    EmbedPunish = discord.Embed(title='Teste')
    EmbedPunish.description = 'Testando'
    
    await interaction.response.send_message(embed=EmbedPunish, ephemeral=True, view=view)
            

     
bot.run(token)