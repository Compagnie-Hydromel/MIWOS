from dotenv import load_dotenv
from db.bootstrap import init
from model.user import User
from model.message import Message
import traceback
load_dotenv()
init()


def user_by_username(username):
    """
    Fetch a user by username.

    :param username: The username of the user to fetch.
    :return: The user object if found, None otherwise.
    """
    user = User.whereFirst(username=username)

    if not user:
        raise ValueError(f"User with username '{username}' not found.")
    return user


def loop():
    """
    Main function to run the application.
    """
    print("Welcome to the interactive MIWOS app!")
    letsgoo = True
    while letsgoo:
        try:
            letsgoo = option()
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print("Traceback:")
            traceback.print_exc()


def option():
    print("\nOptions:")
    print("1. Create a new user")
    print("2. Send a message")
    print("3. List all users")
    print("4. List all messages")
    print("exit. Exit the application")
    choice = input("Enter your choice: ").strip()

    match choice:
        case "1":
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            email = input("Enter email: ").strip()
            firstname = input("Enter firstname: ").strip()
            lastname = input("Enter lastname: ").strip()
            user = User.create(username=username, password=password,
                               email=email, firstname=firstname, lastname=lastname)
            print(f"User {user.username} created successfully.")
        case "2":
            author = user_by_username(
                input("Enter the username of the author: ").strip())
            content = input("Enter message content: ").strip()
            message = Message.create(user=author,
                                     content=content)
            print(
                f"Message from {message.user.username}: {message.content} sent successfully.")
        case "3":
            users = User.all()
            if not users:
                print("No users found.")
            else:
                print("List of users:")
                for user in users:
                    print(f"- {user.username} (ID: {user.id})")
        case "4":
            messages = Message.where(user=user_by_username(
                input("Enter the username of the user: ").strip()))
            if not messages:
                print("No messages found.")
            else:
                print("List of messages:")
                for message in messages:
                    print(
                        f"- {message.user.username}: {message.content} (ID: {message.id})")
        case "exit":
            print("Exiting the application.")
            return False
        case _:
            print("Invalid choice. Please try again.")
    return True


loop()
