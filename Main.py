import types

import requests
import mysql.connector
from pprint import pprint
import json


class obj:

    # constructor
    def __init__(self, dict1):
        self.__dict__.update(dict1)

if __name__ == '__main__':
    username = "BABABABEBEBE"
    url = f"https://api.github.com/users/{username}"
    user_data_json = requests.get(url).json()
    user_data = json.loads(json.dumps(user_data_json), object_hook=obj)
    # pprint(user_data)

    url_rep = "https://api.github.com/users/BABABABEBEBE/repos"
    repository_data_json = requests.get(url_rep).json()
    repository_data = json.loads(json.dumps(repository_data_json), object_hook=obj)


    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1401vasil",
        database="lab2"
    )

    print(mydb)

    mycursor = mydb.cursor()
    sql_user = "INSERT INTO user (name, email, reg_data) VALUES (%s, %s, %s )"
    if user_data.email is None:
        user_data.email = "This user doesnt have email"
    user_data.created_at = user_data.created_at[:-10]
    val_user = (user_data.login, user_data.email, user_data.created_at)
    mycursor.execute(sql_user, val_user)
    mydb.commit()

    for repository in repository_data:
        sql_repository = "INSERT INTO repository ( name, description, cr_data) VALUES (%s, %s, %s )"
        if repository.description is None:
            repository.description = "This repository doesnt have description"
        repository.created_at = repository.created_at[:-10]
        val_repository = (repository.name, repository.description, repository.created_at)
        url_branch = f"https://api.github.com/repos/{username}/{repository.name}/branches"
        branch_data_json = requests.get(url_branch).json()
        branch_data = json.loads(json.dumps(branch_data_json), object_hook=obj)
        mycursor.execute(sql_repository, val_repository)
        mydb.commit()
        for branch in branch_data:
            sql_branch = "INSERT INTO branch ( name, protected) VALUES (%s, %s )"
            val_branch = (branch.name, branch.protected)
            mycursor.execute(sql_branch, val_branch)
            mydb.commit()
            url_file = f"https://api.github.com/repos/{username}/{repository.name}/contents/?ref={branch.name}"
            file_data_json = requests.get(url_file).json()
            file_data = json.loads(json.dumps(file_data_json), object_hook=obj)
            for file in file_data:
                sql_file = "INSERT INTO file ( name, size, path, type) VALUES (%s, %s, %s, %s)"
                val_file = (file.name, file.size,file.path,file.type)
                mycursor.execute(sql_file, val_file)
                mydb.commit()
