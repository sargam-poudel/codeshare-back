import sys
from codeshare.db_init import create_tables, create_super_user
from tortoise import run_async
import pathlib


def create_app(directory):
    path_obj = pathlib.Path() / "miscellaneous"
    for objs in pathlib.Path("").iterdir():
        if objs.name == directory:
            print("directory already exists")
            return
    create_dir = pathlib.Path(directory)
    create_dir.mkdir(parents=True, exist_ok=True)
    for dummy_file in path_obj.iterdir():
        if dummy_file.name == "Readme.md":
            continue
        file_name = dummy_file.name.replace(".txt", ".py")
        path = create_dir / file_name
        with path.open("w", encoding="utf-8") as f:
            if file_name.startswith("urls"):
                f.write(dummy_file.read_text().format(directory, directory, directory))
            else:
                f.write(dummy_file.read_text())


try:
    first, main, *extra = sys.argv
except ValueError:
    pass


def command_create_tables(*args):
    run_async(create_tables())


def createsuperuser(*args):
    username = input("username: ")
    password = input("password:")
    run_async(create_super_user(username, password))


def createsuperuserauto(*args):
    run_async(create_super_user("123", "123"))


commands = {
    "create_tables": [command_create_tables, "creates table on the database"],
    "createsuperuser": [
        createsuperuser,
        "creates a super user by asking username and password",
    ],
    "createsuperuserauto": [
        createsuperuserauto,
        "creates a superuser without asking username or password",
    ],
    "create_app": [create_app, "creates an app to the current working directory"],
}


def manage_help():
    print(
        """
        Welcome to manage.py help down is the list of commands you can use 
        """
    )
    for key, value in commands.items():
        print(f"{key} | {value[1]}")


commands["help"] = [manage_help, "shows all the commands available"]

if values := commands.get(main):
    values[0](*extra)
else:
    print('no such command found run "help" for more')
