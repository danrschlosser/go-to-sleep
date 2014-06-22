
import string
from osascript import osascript

script_name = 'GetNameAndTitleOfActiveWindow.scpt'

with open(script_name) as f:
    scpt = f.read()

def current_window():
    resp = osascript(scpt)
    if  not ',' in resp:
        return '', ''
    app, title = string.split(resp, ',', 1)
    return app, title

