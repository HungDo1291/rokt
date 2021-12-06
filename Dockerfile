FROM python:3.8.12-bullseye

WORKDIR /usr/src/app

COPY . .

EXPOSE 8279

RUN pip install -r requirements.txt

CMD python -m rokt -i "${INPUT_PATH}" -t "${DATABASE_TYPE}" -n "${DATABASE_NAME}" -u "${USER}" -p "${PASSWORD}" -s "${HOST}" -r ${PORT} -c True