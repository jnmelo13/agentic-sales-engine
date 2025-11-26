from core.tool_registry import (
    set_enabled_tools,
    wrap_server_tool_method,
    filter_server_tools
)
from auth.scopes import set_enabled_tools as set_enabled_services
from core.server import server, configure_server_for_http, set_transport_mode
import gdrive.drive_tools, gsheets.sheets_tools

import os

wrap_server_tool_method(server)
services = ['sheets', 'drive']  
set_enabled_services(services)
set_transport_mode('streamable-http')
configure_server_for_http()

server.run(transport="streamable-http", host=os.environ.get('app_port', "localhost"), port=os.environ.get('app_port', 8001))