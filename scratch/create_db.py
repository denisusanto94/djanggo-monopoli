import pymysql

try:
    db = pymysql.connect(host='127.0.0.1', user='root', password='')
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS `monopoly-superapps`")
    print("Database created or already exists.")
    db.close()
except Exception as e:
    print(f"Error: {e}")
