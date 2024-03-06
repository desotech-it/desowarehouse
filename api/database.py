import mariadb
import os
import sys

name = os.environ['DATABASE_NAME']
pool = None

try:
    pool = mariadb.ConnectionPool(
        host=os.environ['DATABASE_HOST'],
        user=os.environ['DATABASE_USER'],
        password=os.environ['DATABASE_PASSWORD'],
        pool_name=name,
        pool_size=8,
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)
