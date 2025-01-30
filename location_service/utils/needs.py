username_index = 0

def get_next_username():

    global username_index
    usernames = [
        "shifteasy",
        "shifteasy2",
        "shifteasy3",
        "shifteasy4",
        "shifteasy5",
        "shifteasy6",
        "shifteasy7",
        "shifteasy8",
        "shifteasy9",
        "shifteasy10",
        "shifteasy11",
        "shifteasy12",
    ]
    username = usernames[username_index]
    username_index = (username_index + 1) % len(usernames)
    return username
