# Docker image for telegram-click (@PythonTelegramClickBot)

FROM python:3.12-slim-bookworm
#-alpine

WORKDIR /app

RUN apt-get update \
 && apt-get -y install git

COPY . .

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy
RUN pip install .

CMD [ "python", "./example.py" ]
