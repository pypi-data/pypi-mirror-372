# Configuration file for running OSITAH with gunicorn as a systemd service

workers = 1
threads = 4
bind = "0.0.0.0:7777"
daemon = False  # don't run as a daemon with systemd
capture_output = True
# loglevel = 'debug'

# Adjust to site specific configuration
accesslog = "/pdisk/ositah/logs/ositah.accesslog"
errorlog = "/pdisk/ositah/logs/ositah.errorlog"
