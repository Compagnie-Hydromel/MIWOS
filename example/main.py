from dotenv import load_dotenv
from db.bootstrap import init
from model.user import User
from model.message import Message

load_dotenv()
init()


def main():
    """
    Main function to run the application.
    """
    pass


if __name__ == "__main__":
    main()
