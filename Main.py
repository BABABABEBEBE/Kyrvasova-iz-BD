import requests
import mysql.connector
import json
import logging
from contextlib import closing
from typing import List, Dict, Any, Optional

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
    sql = "INSERT INTO user (name, email, reg_data, followers, public_repos) VALUES (%s, %s, %s, %s, %s)"
    email = user_data.email if user_data.email else "This user doesn't have an email"
    reg_data = user_data.created_at[:10]
    followers = user_data.followers if hasattr(user_data, 'followers') else 0
    public_repos = user_data.public_repos if hasattr(user_data, 'public_repos') else 0
    execute_query(cursor, sql, (user_data.login, email, reg_data, followers, public_repos))


def insert_repository(cursor, repository: Obj):
    sql = "INSERT INTO repository (name, description, cr_data, stars, forks) VALUES (%s, %s, %s, %s, %s)"
    description = repository.description if repository.description else "No description"
    cr_data = repository.created_at[:10]
    stars = repository.stargazers_count if hasattr(repository, 'stargazers_count') else 0
    forks = repository.forks_count if hasattr(repository, 'forks_count') else 0
    execute_query(cursor, sql, (repository.name, description, cr_data, stars, forks))


def insert_branch(cursor, branch: Obj):
    sql = "INSERT INTO branch (name, protected, last_commit_sha) VALUES (%s, %s, %s)"
    last_commit_sha = branch.commit.sha if hasattr(branch, 'commit') else "Unknown"
    execute_query(cursor, sql, (branch.name, branch.protected, last_commit_sha))


def insert_file(cursor, file: Obj):
    sql = "INSERT INTO file (name, size, path, type, download_url) VALUES (%s, %s, %s, %s, %s)"
    download_url = file.download_url if hasattr(file, 'download_url') else "Not available"
    execute_query(cursor, sql, (file.name, file.size, file.path, file.type, download_url))


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