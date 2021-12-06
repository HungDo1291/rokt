FROM python:3.8.12-bullseye

WORKDIR /usr/src/app

COPY . .

ARG INPUT_PATH=/usr/src/app/rokt/resources/sample1.txt
ARG DATABASE_TYPE=sqlite
ARG DATABASE_NAME=events
ARG USER=root
ARG PASSWORD=my-secret-password
ARG HOST=localhost
ARG PORT=3306

EXPOSE ${PORT}

EXPOSE 8279

RUN pip install -r requirements.txt

RUN python -m rokt.parser -i ${INPUT_PATH} -t ${DATABASE_TYPE} -n ${DATABASE_NAME} -u ${USER} -p ${PASSWORD} -s ${PORT} -s ${HOST} -c True

ENV FLASK_APP rokt/exposer.py

CMD ["flask", "run", "-p", "8279", "-h", "0.0.0.0"]