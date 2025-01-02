FROM odoo:18

COPY --chown=odoo kj /mnt/extra-addons
COPY --chown=odoo enterprise /mnt/enterprise

# Enable those steps, if you want to install python packages (prepare requirements.txt first!)
# COPY --chown=odoo requirements.txt /mnt/requirements.txt

# USER root
# RUN pip install -r /mnt/requirements.txt
# USER odoo