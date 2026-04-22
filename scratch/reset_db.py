import pymysql

try:
    db = pymysql.connect(host='127.0.0.1', user='root', password='')
    cursor = db.cursor()
    cursor.execute("DROP DATABASE IF EXISTS `monopoly-superapps`")
    cursor.execute("CREATE DATABASE `monopoly-superapps`")
    print("Database reset successfully.")
    db.close()
except Exception as e:
    print(f"Error: {e}")
