FROM odoo:15

COPY --chown=odoo addons /mnt/extra-addons
COPY --chown=odoo oca_collection /mnt/oca_collection
COPY --chown=odoo 3p_collection /mnt/3p_collection
COPY --chown=odoo requirements.txt /mnt/requirements.txt

USER root
RUN pip install -r /mnt/requirements.txt
RUN apt update && apt install net-tools procps iproute2 -y

USER odoo