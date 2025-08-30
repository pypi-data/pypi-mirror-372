# PSQL Interface to BlackDynamite (deprecated)

## Register hosts to BlackDynamite

In the .blackdynamite folder (in your home) you should add the servers where your databases are, with the option and information of your choice.

For each database you can add a file .bd of the name of the server (or an alias and specify the host inside:

```bash
host = yourHost.domain.countryID
```

It is also recommended to specify the password of the database to avoid typing it when using auto-completion.

Here is an example of a valid blackdynamite config file:

```bash
cat ~/.blackdynamite/lsmssrv1.epfl.ch.bd
```

```bash
host = lsmssrv1.epfl.ch
password = XXXXXXXXX 
```

## Installation of the server side: setting up the PostGreSQL database (for admins)

If you want to setup a PostGreSQL server to store BlackDynamite data,
then you have to follow this procedure.

Install the PSQL server:
```bash
sudo apt-get install postgresql-9.4
```

You know need privileges to create databases and users.
This can be done using the following:

You should add a database named blackdynamite (only the first time):
```bash
psql --command "CREATE USER blackdynamite WITH PASSWORD '';"
createdb -O blackdynamite blackdynamite
```

## Adding a user

You should create a user:
```bash
psql --command "CREATE USER mylogin WITH PASSWORD 'XXXXX';"
```

And add permissions to create tables to the user
```bash
psql --command "grant create on database blackdynamite to mylogin"
```

This can also be done with the commodity tool
```bash
createUser.py --user admin_user --host hostname
```

## Useful Postgresql commands

How to list the available schemas ?
```psql
> \dn
```

How to get into the schema or the study ?
```psql
> set search_path to schema_name;
> set search_path to study_name;
```


How to list all the tables ?
```psql
> \d
```
or 
```psql
> SELECT * FROM pg_catalog.pg_tables;
```



How to list entries from a table (like the jobs) ?
```psql
> SELECT * from table_name ;
```

How to list all the databases ?
```psql
> \l
```

How to list the available databases ?

```psql
> select datname from pg_catalog.pg_database;
```

How to know the current database ?

```psql
> select current_database();
```
