from db_management import loop as db_management
from dotenv import load_dotenv
from db.bootstrap import init
from model.user import User
from model.message import Message
from model.channel import Channel
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


def channel_by_name(name):
    """
    Fetch a channel by name.

    :param name: The name of the channel to fetch.
    :return: The channel object if found, None otherwise.
    """
    channel = Channel.whereFirst(name=name)

    if not channel:
        raise ValueError(f"Channel with name '{name}' not found.")
    return channel


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
    print("2. create a channel")
    print("3. Send a message")
    print("4. List all users")
    print("5. List all messages")
    print("6. List all channels")
    print("7. Show user channels")
    print("8. Show channel users")

    print("db. Database management")
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
            print(f"User '{user}' created successfully.")
        case "2":
            channel_name = input("Enter channel name: ").strip()
            channel = Channel.create(name=channel_name)
            print(f"Channel '{channel.name}' created successfully.")

        case "3":
            author = user_by_username(
                input("Enter the username of the author: ").strip())
            content = input("Enter message content: ").strip()
            message = Message.create(user=author,
                                     content=content)
            print(
                f"Message from {message.user.username}: {message.content} sent successfully.")
        case "4":
            users = User.all()
            if not users:
                print("No users found.")
            else:
                print("List of users:")
                for user in users:
                    print(f"- {user}")
        case "5":
            messages = user_by_username(
                input("Enter the username of the user: ").strip()).messages
            if not messages:
                print("No messages found.")
            else:
                print("List of messages:")
                for message in messages:
                    print(
                        f"- {message.user.username}: {message.content} (ID: {message.id})")
        case "6":
            channels = Channel.all()
            if not channels:
                print("No channels found.")
            else:
                print("List of channels:")
                for channel in channels:
                    print(f"- {channel.name} (ID: {channel.id})")
        case "7":
            users = channel_by_name(
                input("Enter the name of the channel: ").strip()).users
            if not users:
                print("No users found in this channel.")
            else:
                print("Users in this channel:")
                for user in users:
                    print(f"- {user})")
        case "8":
            channels = user_by_username(
                input("Enter the username of the user: ").strip()).channels
            if not channels:
                print("No channels found in this user.")
            else:
                print("Channels of this users:")
                for channel in channels:
                    print(f"- {channel})")
        case "db":
            db_management()
        case "exit":
            print("Exiting the application.")
            return False
        case _:
            print("Invalid choice. Please try again.")
    return True


loop()
