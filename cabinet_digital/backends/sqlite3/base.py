from django.db.backends.sqlite3.base import DatabaseWrapper as BaseDatabaseWrapper

class DatabaseWrapper(BaseDatabaseWrapper):
    def get_new_connection(self, conn_params):
        conn = super().get_new_connection(conn_params)
        # Set pragmas here
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA cache_size=-64000')
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('PRAGMA ignore_check_constraints=OFF')
        conn.execute('PRAGMA synchronous=NORMAL')
        return conn 