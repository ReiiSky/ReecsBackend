import psycopg2

conn = psycopg2.connect(
        database="reecs",
        user = "postgres",
        password = "reecs-password",
        host = "127.0.0.1",
        port = "5432",
    )

conn.autocommit = True
