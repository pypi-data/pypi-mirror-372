def format_message(msg: str, color: str) -> str:
    # Function to format the log message with color
    return f'<span style="color: {color};">{msg}</span>'


def manage_file_output(directory: str, filename: str, content: str) -> None:
    # Function to manage writing content to a file
    with open(f"{directory}/{filename}", "a") as file:
        file.write(content + "\n")
