# 1 Deployment instructions


## 1.1 Build the image
- `docker build -t <imagename:tag> .` . For example `docker build -t rokt:v1 .`
## 1.2 Run the container
### 1.2.1 Commands

- Test with inbuilt sqlite database: `docker run -it --name <container_name>  -p 8279:8279 -e INPUT_PATH=<input_path> -e DATABASE_TYPE=sqlite <image_name:tag>`
- Production with an external SQL database: `docker run -it --name <container_name> -p 8279:8279 -e INPUT_PATH=<input_path> -e DATABASE_TYPE=<database_type> -e DATABASE_NAME=<database_name> -e USER=<user_name> -e PASSWORD=<password> -e HOST=<host> -e PORT=<port> -c <True/False>  <image_name>:<tag>`
- If you store the input files externally, you can mount the folder to docker container by `-v /path_to_yourfoler:/usr/src/app/input_or_any_where_else`. 

Examples:

- Test with internal sample input files and sqlite: `docker run -it --name rokt_container_test  -p 8279:8279 -e INPUT_PATH=/usr/src/app/rokt/res
ources/*.txt -e DATABASE_TYPE=sqlite rokt:v1`
- Production  with a locally hosted SQL database (tested on Window): `docker run -it --name rokt_container_prod -p 8279:8279 -e INPUT_PATH=/usr/src/app/rokt/resource
s/*.txt -e DATABASE_TYPE=mysql+pymysql -e DATABASE_NAME=my_db_name -e USER=root -e PASSWORD=my_password -e HOST=host.docker.internal
 -e PORT=3306 rokt:v1`


### 1.2.2 Parameters

- INPUT_PATH: Path to the input file inside the container. If you have more than one file, you can use regex `*` such as `path/*.txt`. If you store the input file(s) externally, you can mount the folder when running the container. TODO: test AWS S3 bucket path.
- DATABASE_TYPE: This app can ideally connect to any types of external database, be it MySQL or PostgreSQL, Redshift, BigQuery, etc. 
At the moment two types of database are tested: `mysql+pymysql` and `sqlite` (sqlite is stored in this repo just for testing).
- DATABASE_NAME: The database name
- USER: The username for the database
- PASSWORD: The password for the database user
- HOST: The database host. To connect to locally hosted SQL server, set to `host.docker.internal` (tested on Windows). To connect to AWS RDS for example, set the host to the RDS endpoint, for example `database-name.abcdefghijkkk.ap-southeast-2.rds.amazonaws.com`.
- PORT: The port for the database. The default of MariaDB is `3306`.

# 2 Application usage
In order to send a request to the API server, you can use the command
`curl -X POST localhost:8279/ -d "{\"filename\":\"sample1.txt\", \"from\":\"1998-07-06T23:00:00Z\", \"to\": \"2020-07-06T23:00:00Z\"}"  --header "Content-Type: applica
tion/json"`

# 3 Software details

## 3.1 Data Pipeline

- The parser module parse data from input files to the SQL database. Command: `python -m rokt.parser -i <inputpath> -t <database_type> -n <database_name> -u <user> -p <password> -s <host> -r <port> -c <True/False>`. If set `-c False`, the SQL commands will not be executed (used when testing). 
