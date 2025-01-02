FROM python:3.9-slim

COPY python /opt/custom/python

WORKDIR /opt/custom/python

RUN pip install --no-cache-dir -r requirements.txt

CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"