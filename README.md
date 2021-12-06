# Deployment instructions

## Parameters:
- INPUT_PATH: Path to the input file inside the container. If you have more than one file, you can use regex `*` such as `path/*.txt`. If you store the input file(s) externally, you can mount the folder when running the container (see below).
- DATABASE_TYPE: This app can ideally connect to any types of external database, be it MySQL or PostgreSQL, Redshift, BigQuery, etc. 
At the moment two types of database are tested: `mysql+pymysql` and `sqlite` (sqlite is stored in this repo just for testing).
## Build the image
- PROD: `docker build -t rokt:v1 .`
- TEST: `docker build -t rokt:v1 --build-arg INPUT_PATH=/usr/src/app/rokt/resources/sample1.txt --bu
ild-arg DATABASE_TYPE=sqlite .`
## Run the container
- `docker run -it --name rokt_v1 -p 8279:8279 rokt:v1`
- If you store the input files externally, you can mount the folder to docker container by `-v /path_to_yourfoler:/usr/src/app/input_or_any_where_else`.

# Application usage
In order to curl the server, you can use the command
`curl -X POST localhost:8279/ -d "{\"filename\":\"sample1.txt\", \"from\":\"1998-07-06T23:00:00Z\", \"to\": \"2020-07-06T23:00:00Z\"}"  --header "Content-Type: applica
tion/json"`

# Software details

## Data Pipeline

- production with externally connected database: `python -m rokt.parser -i <inputpath> -t <database_type> -n <database_name> -u <user> -p <password> -s <host> -r <port> -c <True/False>`

- test with the inbuilt sqlite database in this repo: `python -m roke.parser -i <inputpath> -t sqlite -c <True/False>` 
