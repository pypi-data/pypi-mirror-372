def intput(msg: str) -> int:
    """Read an integer from user input with a message prompt."""
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("Invalid input! Please enter an integer.")
