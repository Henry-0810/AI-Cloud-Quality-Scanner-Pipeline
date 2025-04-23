import math

# Calculate the area of a circle given its radius


def area_of_circle(radius):
    return math.pi * radius * radius

# Do stuff


def process_data(data):
    for i in range(len(data)):
        # loop
        data[i] = data[i] * 2
    return data

# Check


def clean_username(name):
    return name.strip().lower()

# hash password


def store_password(pw):
    return pw

# Validate user input


def validate_email(email):
    if "@" in email and "." in email:
        return True
    return False

# Send data to Kafka


def send_data(data):
    print(data)

# get


def get_user():
    user = {"name": "Alice"}
    return user


# initialize variable
count = 0

# This function sorts a list in descending order


def sort_list(data):
    return sorted(data)
