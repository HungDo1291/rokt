# Introduction
`rokt` is an application that parses input files from a specified folder into a SQL database. The app then run an API server for querying that database with POST requests. The output is in json format.

This app does not use any raw SQL commands, thus can ideally connect to an external database with any types of SQL dialect, be it MySQL or PostgreSQL, Redshift, BigQuery, etc. 
At the moment two types of database are tested: `mysql+pymysql` (localhosted and AWS RDS) and `sqlite` (sqlite is stored in this repo just for testing). 

This app reads every input files in chunks of 10,000 lines each. For a file of a few GBs, one does not really have to parallelize. However I added the parallelization.

# Business assumptions
- The input files are stored in a folder that can be mounted to the container
- For every operation, the table `events` is dropped if existed and then recreated afresh.
- All rows with incorrect or empty time are dropped.

# Deployment instructions

## Build the image
- Command: `docker build -t <image_name:tag> .` . For example: `docker build -t rokt:v1 .`.
## Run the container
### a) Commands
- Test with inbuilt sqlite database: `docker run -it --name <container_name>  -p 8279:8279 -e INPUT_PATH=<input_path> -e DATABASE_TYPE=sqlite <image_name:tag>`
- Production with an external SQL database: `docker run -it --name <container_name> -p 8279:8279 -e INPUT_PATH=<input_path> -e DATABASE_TYPE=<database_type> -e DATABASE_NAME=<database_name> -e USER=<user_name> -e PASSWORD=<password> -e HOST=<host> -e PORT=<port> -c <True/False>  <image_name>:<tag>`
- If you store the input files externally, you can mount the folder to docker container by `-v /path_to_yourfoler:/usr/src/app/input_or_any_where_else`. 

### b) Examples
- For testing, simply run `docker run -it --name rokt_container_test  -p 8279:8279 rokt:v1` 
and the default values will be used, running sample input files and test sqlite database in this repository.
- Fot testing with the inbuilt `sqlite` but with different input files: `docker run -it --name rokt_container_test  -p 8279:8279 -v /external_path_to_yourfoler:/usr/src/app/input -e INPUT_PATH=/usr/src/app/input/*.txt -e DATABASE_TYPE=sqlite rokt:v1`.
- For production  with a locally hosted SQL database (tested on Window): `docker run -it --name rokt_container_prod -p 8279:8279 -e INPUT_PATH=/usr/src/app/rokt/resources/*.txt -e DATABASE_TYPE=mysql+pymysql -e DATABASE_NAME=my_db_name -e USER=root -e PASSWORD=my_password -e HOST=host.docker.internal
 -e PORT=3306 rokt:v1`
- To connect to AWS RDS for example, set the host to the RDS endpoint, for example `database-name.abcdefghijkkk.ap-southeast-2.rds.amazonaws.com`.

### c) Parameters

- INPUT_PATH: Path to the input file inside the container. If you have more than one file, you can use regex `*` such as `path/*.txt`. Default value is `/usr/src/app/rokt/resources/*.txt`. 
- DATABASE_TYPE: Type of database, for example `mysql+pymysql`. Default value is `sqlite`.
- DATABASE_NAME: The database name. Default value is `events`.
- USER: The username for the database. Default value is `root`.
- PASSWORD: The password for the database user. Default value is `my_pass`.
- HOST: The database host. Default value is `host.docker.internal`.
- PORT: The port for the database. Default value is `3306` (default port of MariaDB). 

# 2 Application usage
In order to send a request to the API server, you can use the command
`curl -X POST localhost:8279/ -d "{\"filename\":\"sample1.txt\", \"from\":\"1998-07-06T23:00:00Z\", \"to\": \"2020-07-06T23:00:00Z\"}"  --header "Content-Type: application/json"`

# 3 Software details

## 3.1 Data Pipeline

- The parser module parse data from input files to the SQL database. Command: `python -m rokt.parser -i <inputpath> -t <database_type> -n <database_name> -u <user> -p <password> -s <host> -r <port> -c <True/False>`. If set `-c False`, the SQL commands will not be executed (used when testing). 
