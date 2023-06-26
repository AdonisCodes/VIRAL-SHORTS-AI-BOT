from datetime import datetime


# Function to Parse a date String
def parse_datetime(date_string):
    # Parsing A date String
    print("Parsing date and time...")
    datetime_obj = datetime.strptime(date_string, "%b %d, %Y | %H:%M")
    new_date = datetime_obj.strftime("%b %d, %Y")
    new_time = datetime_obj.strftime("%H:%M")
    return {"new_date": new_date, "new_time": new_time}


# Function to parse a Video Link
def parse_vlink(link):
    print("Extracting video id...")
    return link[len(link) - 11:]
