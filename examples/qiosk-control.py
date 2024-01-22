import asyncio
import websockets
import json
from docopt import docopt
from websockets.client import WebSocketClientProtocol

docopt_config = """
Qiosk command console.

License: GPL-3.0
Website: https://github.com/Salamek/chromium-kiosk

Command details:
    setUrl                 Set displayed url.
    setWindowMode          Sets window mode.
    setIdleTime            Set idle time.
    setWhiteList           Set white list items.
    setPermissions         Set permissions.
    setNavbarVerticalPosition  Set navbar vertical position.
    setNavbarHorizontalPosition Set navbar horizontal position.
    setNavbarWidth         Set navbar width.
    setNavbarHeight        Set navbar height.
    setDisplayAddressBar   Set display address bar.
    setDisplayNavBar       Set display navbar.
    setUnderlayNavBar      Set underlay navbar.
    getConfiguration       Returns configuration.
    exit                   Exit the interface.
Usage:
    q setUrl <url>
    q setWindowMode <fullscreen>
    q setIdleTime <idleTime>
    q setWhiteList [<whitelist>...]
    q setPermissions [<permissions>...]
    q setNavbarVerticalPosition <navbarVerticalPosition>
    q setNavbarHorizontalPosition <navbarHorizontalPosition>
    q setNavbarWidth <navbarWidth>
    q setNavbarHeight <navbarHeight>
    q setDisplayAddressBar <displayAddressBar>
    q setDisplayNavBar <displayNavBar>
    q setUnderlayNavBar <underlayNavBar>
    q getConfiguration
    q exit
"""

allowed_commands = [
    'setUrl',
    'setWindowMode',
    'setIdleTime',
    'setWhiteList',
    'setPermissions',
    'setNavbarVerticalPosition',
    'setNavbarHorizontalPosition',
    'setNavbarWidth',
    'setNavbarHeight',
    'setDisplayAddressBar',
    'setDisplayNavBar',
    'setUnderlayNavBar',
    'getConfiguration',
    'exit'
]


async def send_message(websocket: WebSocketClientProtocol):
    while True:
        command_parts = input('Enter command: ').split(' ')
        command_options = docopt(docopt_config, command_parts)

        command_name = None
        for allowed_command in allowed_commands:
            if command_options.get(allowed_command, False):
                command_name = allowed_command
                break

        if not command_name:
            raise Exception('Unknown command')

        if command_name == 'exit':
            exit()

        data = {}
        for option_name, option_value in command_options.items():
            if option_name.startswith('<') and option_name.endswith('>'):
                if option_value == 'true':
                    option_value = True
                elif option_value == 'false':
                    option_value = False
                data[option_name.replace('<', '').replace('>', '')] = option_value

        command = json.dumps({
            'command': command_name,
            'data': data
        })

        await websocket.send(command)
        await asyncio.sleep(1)


async def receive_message(websocket: WebSocketClientProtocol):
    print('Receiving')
    while True:
        response = await websocket.recv()
        print(response)


async def main():
    uri = "ws://localhost:1791"
    async with websockets.connect(uri) as websocket:
        asyncio.create_task(send_message(websocket))
        asyncio.create_task(receive_message(websocket))
        await asyncio.Future()

asyncio.run(main())
