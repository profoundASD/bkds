from flask import Flask, jsonify
from flask_cors import CORS
import psutil
import platform

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app = Flask(__name__)

def get_ram_info():
    ram = psutil.virtual_memory()
    return {'total': ram.total, 'used': ram.used, 'percent': ram.percent}

def get_cpu_info():
    cpu = {'cores': psutil.cpu_count(), 'frequency': psutil.cpu_freq().current}
    return cpu

def get_network_info():
    interfaces = psutil.net_if_stats()
    
    # Check available interfaces and determine connection type
    if 'eth0' in interfaces and interfaces['eth0'].isup:
        connection_type = "Ethernet"
    elif 'wlan0' in interfaces and interfaces['wlan0'].isup:
        connection_type = "WiFi"
    else:
        connection_type = "Unknown"

    # Placeholder for network strength as it's not straightforward to obtain
    connection_strength = "Not Available"

    return {'type': connection_type, 'strength': connection_strength}


def get_battery_info():
    if hasattr(psutil, "sensors_battery"):
        battery = psutil.sensors_battery()
        if battery:
            return {'percent': battery.percent, 'plugged_in': battery.power_plugged}
    return "Battery information not available"

@app.route('/systeminfo')
def system_info():
    return jsonify({
        'RAM': get_ram_info(),
        'CPU': get_cpu_info(),
        'Network': get_network_info(),
        'Battery': get_battery_info()
    })

if __name__ == '__main__':
    app.run(debug=True)
