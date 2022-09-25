# Docker image for telegram-click (@PythonTelegramClickBot)

FROM python:3.10
#-alpine

WORKDIR /app

RUN apt-get update

COPY . .

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy
RUN pip install .

CMD [ "python", "./example.py" ]
