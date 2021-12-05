# Parser
prod: `python -m rokt.parser -i <inputpath> -t <database_type> -n <database_name> -u <user> -p <password> -s <host> -r <port> (-c)`
test: `python -m roke.parser -i <inputpath> -t sqlite` - automatically use the sqlite database stored in this repo

`curl -X POST localhost:8279/ -d "{\"filename\":\"sample1.txt\", \"from\":\"1998-07-06T23:00:00Z\", \"to\": \"2020-07-06T23:00:00Z\"}"  --header "Content-Type: applica
tion/json"`