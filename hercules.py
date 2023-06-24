import os
from client import client

for filename in os.listdir('./c_hercules'):
    if filename.endswith('.py'):
        client.load_extension(f'c_hercules.{filename[:-3]}')
        
client.run('YOUR BOT TOKEN HERE')