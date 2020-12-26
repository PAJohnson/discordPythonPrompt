import discord
from io import StringIO
import sys
import traceback
from stopit import SignalTimeout as Timeout, signal_timeoutable as timeoutable

client = discord.Client()
globals()['inUse'] = False
globals()['msg'] = None

async def handle_content(message, situation):
    if message.content.startswith('$pyrun '):
        cmd = message.content.split('$pyrun ')
        if len(cmd) == 1:
            return
        linesOld = cmd[1].splitlines(True)
        lines = []
        for line in linesOld:
            if not '```' in line:
                lines.append(line)
            
        newCmd = ''.join(lines)
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = sys.stdout = StringIO()
        redirected_err = sys.stderr = StringIO()
        with Timeout(30.0, swallow_exc=False) as timeout_ctx:
            exec(newCmd)
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        if globals()['inUse'] and situation == "edit":
            await globals()['msg'].edit(content='```'+redirected_output.getvalue()+redirected_err.getvalue()+'```')
        else:
            globals()['inUse'] = True
            globals()['msg'] = await message.channel.send('```'+redirected_output.getvalue()+redirected_err.getvalue()+'```')

    elif message.content.startswith('$py'):
        cmd = message.content.split('$py ')
        if len(cmd) == 1:
        	return
        retVal = ''
        with Timeout(30.0, swallow_exc=False) as timeout_ctx:
            retVal = str(eval(cmd[1]))
        await message.channel.send(retVal)
        
    else:
        globals()['inUse'] = False

@client.event      
async def on_message_edit(before, after):
    if before.author == client.user:
        return

    await handle_content(after,"edit")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await handle_content(message,"new")
    
@client.event
async def on_error(event, *args, **kwargs):
    message = args[0] #Gets the message object
    if globals()['inUse']:
        await globals()['msg'].edit(content=traceback.format_exc())
    else:
        globals()['inUse'] = True
        globals()['msg'] = await message.channel.send(traceback.format_exc())
        
        
if __name__ == "__main__":
    secret = ''
    with open('discordKey.txt', 'r') as f:
        secret = f.read().rstrip()
    client.run(secret)
