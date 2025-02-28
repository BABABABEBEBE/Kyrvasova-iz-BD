import requests
import mysql.connector
import json


class Obj:
    def __init__(self, dict1):
        self.__dict__.update(dict1)


def fetch_data(url):
    response = requests.get(url)
    return json.loads(json.dumps(response.json()), object_hook=Obj)


def insert_user(cursor, user_data):
    sql = "INSERT INTO user (name, email, reg_data) VALUES (%s, %s, %s)"
    email = user_data.email if user_data.email else "This user doesn't have an email"
    reg_data = user_data.created_at[:10]  # Trim timestamp
    cursor.execute(sql, (user_data.login, email, reg_data))


def insert_repository(cursor, repository):
    sql = "INSERT INTO repository (name, description, cr_data) VALUES (%s, %s, %s)"
    description = repository.description if repository.description else "No description"
    cr_data = repository.created_at[:10]
    cursor.execute(sql, (repository.name, description, cr_data))


def insert_branch(cursor, branch):
    sql = "INSERT INTO branch (name, protected) VALUES (%s, %s)"
    cursor.execute(sql, (branch.name, branch.protected))


def insert_file(cursor, file):
    sql = "INSERT INTO file (name, size, path, type) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (file.name, file.size, file.path, file.type))


def main():
    username = "BABABABEBEBE"

    # Database connection
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1401vasil",
        database="lab2"
    )
    cursor = mydb.cursor()

    # Fetch and insert user data
    user_data = fetch_data(f"https://api.github.com/users/{username}")
    insert_user(cursor, user_data)

    # Fetch and insert repositories
    repositories = fetch_data(f"https://api.github.com/users/{username}/repos")
    for repository in repositories:
        insert_repository(cursor, repository)

        # Fetch and insert branches
        branches = fetch_data(f"https://api.github.com/repos/{username}/{repository.name}/branches")
        for branch in branches:
            insert_branch(cursor, branch)

            # Fetch and insert files
            files = fetch_data(f"https://api.github.com/repos/{username}/{repository.name}/contents/?ref={branch.name}")
            for file in files:
                insert_file(cursor, file)

    # Commit all changes and close connection
    mydb.commit()
    cursor.close()
    mydb.close()


if __name__ == "__main__":
    main()
