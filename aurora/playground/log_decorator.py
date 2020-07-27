def log_dec(debug_level):
    def logger(func, message):
        func()
        print(func.__name__, f"{debug_level}: {message}")

    return logger


def click_one():
    # logic here
    print("Clicked a button!")


log_one = log_dec("DEBUG")
log_two = log_dec("ERROR")
log_one(click_one, "executed!")
log_two(click_one, "Heey")
log_one(click_one, "executed!")
