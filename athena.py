import os
from client import client

for filename in os.listdir('./c_athena'):
    if filename.endswith('.py'):
        client.load_extension(f'c_athena.{filename[:-3]}')
        
client.run('YOUR BOT TOKEN HERE')