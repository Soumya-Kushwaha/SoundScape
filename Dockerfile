FROM python:3.8-slim


RUN apt-get update && apt-get install -y \ 
    portaudio19-dev \ 
    gcc \
    tk

COPY requirements.txt .

COPY . .

ENV PIP_ROOT_USER_ACTION=ignore

RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt


CMD ["Spectogram.py"]
ENTRYPOINT ["python3"]
