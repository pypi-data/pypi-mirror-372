# gunicorn configuration examples

The files in this directory provide 3 files to manage OSITAH application with gunicorn:

- gunicorn@.service: the systemd script to manage gunicorn with systemd. It is a multi-instance service and OSITAH is typically managed with the unit `gunicorn@ositah`.
- gunicorn.ositah: a file typically placed in `/etc/sysconfig` and defining the paramters specifich to OSITAH gunicorn instance
- app.conf.py: the gunicorn parameters used to start the OSITAH instance

All these files must be considered as templates. In particular, the various paths must be customized according to your site configuration.
