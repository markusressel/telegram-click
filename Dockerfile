# Docker image for telegram-click (@PythonTelegramClickBot)

FROM python:3.6
#-alpine

WORKDIR /app

RUN apt-get update

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./example.py" ]