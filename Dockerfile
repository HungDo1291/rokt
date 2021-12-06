FROM python:3.8.12-bullseye

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

ARG INPUT_PATH=${INPUT_PATH}
ARG DATABASE_TYPE=${DATABASE_TYPE}


RUN python -m rokt.parser -i ${INPUT_PATH} -t ${DATABASE_TYPE} -c True

ENV FLASK_APP rokt/exposer.py

EXPOSE 8279

CMD ["flask", "run", "-p", "8279", "-h", "0.0.0.0"]