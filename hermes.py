import os
from client import client

for filename in os.listdir('./c_hermes'):
    if filename.endswith('.py'):
        client.load_extension(f'c_hermes.{filename[:-3]}')
        
client.run('YOUR BOT TOKEN HERE')