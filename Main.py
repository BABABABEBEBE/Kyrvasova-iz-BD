import requests
import mysql.connector
import json
import logging
from contextlib import closing
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Obj:
    def __init__(self, dict1: Dict[str, Any]):
        self.__dict__.update(dict1)


def fetch_data(url: str) -> List[Obj]:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return json.loads(json.dumps(response.json()), object_hook=Obj)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return []


def execute_query(cursor, sql: str, values: tuple):
    try:
        cursor.execute(sql, values)
        logging.info(f"Executed query: {sql} with values {values}")
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")


def insert_user(cursor, user_data: Obj):
    sql = "INSERT INTO user (name, email, reg_data) VALUES (%s, %s, %s)"
    email = user_data.email if user_data.email else "This user doesn't have an email"
    reg_data = user_data.created_at[:10]
    execute_query(cursor, sql, (user_data.login, email, reg_data))


def insert_repository(cursor, repository: Obj):
    sql = "INSERT INTO repository (name, description, cr_data) VALUES (%s, %s, %s)"
    description = repository.description if repository.description else "No description"
    cr_data = repository.created_at[:10]
    execute_query(cursor, sql, (repository.name, description, cr_data))


def insert_branch(cursor, branch: Obj):
    sql = "INSERT INTO branch (name, protected) VALUES (%s, %s)"
    execute_query(cursor, sql, (branch.name, branch.protected))


def insert_file(cursor, file: Obj):
    sql = "INSERT INTO file (name, size, path, type) VALUES (%s, %s, %s, %s)"
    execute_query(cursor, sql, (file.name, file.size, file.path, file.type))


def main():
    username = "BABABABEBEBE"

    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "1401vasil",
        "database": "lab2",
        "autocommit": True
    }

    try:
        with closing(mysql.connector.connect(**db_config)) as mydb, closing(mydb.cursor()) as cursor:
            logging.info("Connected to database")

            user_data = fetch_data(f"https://api.github.com/users/{username}")
            if user_data:
                insert_user(cursor, user_data)

            repositories = fetch_data(f"https://api.github.com/users/{username}/repos")
            for repository in repositories:
                insert_repository(cursor, repository)

                branches = fetch_data(f"https://api.github.com/repos/{username}/{repository.name}/branches")
                for branch in branches:
                    insert_branch(cursor, branch)

                    files = fetch_data(
                        f"https://api.github.com/repos/{username}/{repository.name}/contents/?ref={branch.name}")
                    for file in files:
                        insert_file(cursor, file)

            logging.info("Database operations completed successfully")
    except mysql.connector.Error as err:
        logging.error(f"Database connection error: {err}")

    logging.info("Script execution finished")


if __name__ == "__main__":
    main()
