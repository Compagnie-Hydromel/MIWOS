import traceback
import MIWOS.db as db


def loop():
    """
    Main function to run the application.
    """
    print("Unteractive DB Management!")
    letsgoo = True
    while letsgoo:
        try:
            letsgoo = option()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print("Traceback:")
            traceback.print_exc()


def option():
    print("\nOptions:")
    print("1. migrate")
    print("2. rollback")
    print("back. Back to main menu")

    choice = input("Enter your choice: ").strip()
    match choice:
        case "1":
            db.migrate()
            print("Database migration completed.")
        case "2":
            depth = input("Enter the depth of rollback (default 1): ").strip()
            db.rollback(depth=int(depth) if depth else 0)
            print("Database rollback completed.")
        case "back":
            return False
        case _:
            print("Invalid choice. Please try again.")

    return True
