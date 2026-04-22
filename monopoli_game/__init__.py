import pymysql

pymysql.install_as_MySQLdb()

# Now we can import django modules after pymysql is installed as MySQLdb
try:
    from django.db.backends.mysql import base
    # Workaround for MariaDB 10.4 (Django 5.x requires 10.5+)
    base.DatabaseWrapper.check_database_version_supported = lambda self: None
    
    # Disable RETURNING for MariaDB 10.4
    from django.db.backends.mysql.features import DatabaseFeatures
    DatabaseFeatures.can_return_columns_from_insert = property(lambda self: False)
    DatabaseFeatures.can_return_rows_from_bulk_insert = property(lambda self: False)
    
except Exception:
    pass
