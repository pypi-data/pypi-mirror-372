# Author : Puji Anugrah Pangestu #
# Created : 01 Oct 2022 #
import jwt
import logging
import os
import string
import random
from datetime import datetime, timedelta


def replace_last_character(string, find, replace):
    reversed = string[::-1]
    replaced = reversed.replace(find[::-1], replace[::-1], 1)
    return replaced[::-1]

def calculate_duration(given_time_str, end_time_str=None):
    try:
        # Parse the given time string into a time object
        given_time = datetime.strptime(str(given_time_str), '%H:%M:%S').time()

        # Parse the end time string into a time object if provided, otherwise use the current time
        if end_time_str:
            end_time = datetime.strptime(str(end_time_str), '%H:%M:%S').time()
        else:
            end_time = datetime.now().time()

        # Get today's date
        today = datetime.now().date()

        # Combine today's date with the given time and end time
        given_datetime = datetime.combine(today, given_time)
        end_datetime = datetime.combine(today, end_time)

        # Calculate the time difference
        if end_datetime < given_datetime:
            # If the end time is before the given time, assume the end time is on the next day
            end_datetime += timedelta(days=1)

        time_difference = end_datetime - given_datetime

        # Extract hours, minutes, and seconds from the time difference
        total_seconds = int(time_difference.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours} hours, {minutes} minutes"

    except ValueError:
        return "Duration not shown"


def convert_time(time_str):
    if time_str is not None:
        formatted_time = time_str.strftime("%H:%M")
        return formatted_time
    return ''


def calculate_of_date(is_office_hour, start_date, end_date, holiday_date):
    # get current year
    current_year = datetime.now().year

    # variable
    weekend_dates = []
    leave_dates = []
    result_dates = []

    # format date
    date_from = datetime.strptime(start_date, "%Y-%m-%d")
    date_to = datetime.strptime(end_date, "%Y-%m-%d")

    # get range date from start date to end date
    current_date = date_from
    while current_date <= date_to:
        leave_dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    # Create a date object for January 1st of the specified year
    date = datetime(current_year, 1, 1)

    # Iterate through the days of the year
    while date.year == current_year:
        # Check if the day is a Saturday (5) or Sunday (6)
        if date.weekday() in (5, 6):
            weekend_dates.append(date.strftime("%Y-%m-%d"))  # Add the date to the list
        date += timedelta(days=1)  # Move to the next day

    # Convert the weekend dates to a set for efficient membership testing
    weekend_set = set(weekend_dates)

    if is_office_hour:
        # Create a new list of leave dates excluding those that are in the weekend dates
        filtered_leave = [date for date in leave_dates if date not in weekend_set if date not in holiday_date]
    else:
        filtered_leave = [date for date in leave_dates]

    # Print the filtered list of leave dates
    for date in filtered_leave:
        result_dates.append(date)

    return len(result_dates)


def working_date():
    works_dates = []
    # Get the current date
    current_date = datetime.now()

    # Calculate the first day of the current month
    first_day_of_month = current_date.replace(day=1)

    # Calculate the last day of the current month
    next_month = current_date.replace(day=28) + timedelta(days=4)
    last_day_of_month = next_month - timedelta(days=next_month.day)

    # Initialize a list to store the dates of the current month
    current_month_dates = []

    # Iterate through the days of the current month
    current_day = first_day_of_month
    while current_day <= last_day_of_month:
        # Check if the day is not a weekend (Monday to Friday)
        if current_day.weekday() < 5:
            current_month_dates.append(current_day.strftime("%Y-%m-%d"))
        current_day += timedelta(days=1)

    # Print the list of dates for the current month (excluding weekends)
    for date in current_month_dates:
        works_dates.append(date)

    return works_dates


def get_current_date():
    # Get the current date
    current_date = datetime.now()

    # Format the current date as "yyyy-MM-dd"
    formatted_date = current_date.strftime("%Y-%m-%d")

    return formatted_date


def get_date_range(date_from_str, date_to_str):
    #date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
    #date_to = datetime.strptime(date_to_str, '%Y-%m-%d')
    date_from = date_from_str
    date_to = date_to_str

    date_range = []
    current_date = date_from
    while current_date <= date_to:
        date_range.append(current_date)
        current_date += timedelta(days=1)
    return date_range

class SystemFunction:
    def generate_random_name(self):
        characters = list(string.ascii_letters + string.digits)
	    ## length of name from the user
        length = int(20)

    	## shuffling the characters
        random.shuffle(characters)

    	## picking random characters from the list
        name = []
        for i in range(length):
            name.append(random.choice(characters))

        ## shuffling the resultant name
        random.shuffle(name)

        return("".join(name))
		
class EncodeUrl:
    def encode_url(url):
        obj = dict(
            url=url
        )
        encodes = jwt.encode(obj, os.environ.get("JWT_TOKEN"), algorithm='HS256')
		
        # Start condition different in linux and windows #
        try:
            encodes = encodes.decode("utf-8")
        except:
            encodes = encodes
        # End condition different in linux and windows #
        return encodes
		
    def create_folder(folder_name):
        base_path = folder_name
        try:
            os.makedirs(base_path)
        except:
            logging.error(f"This folder {base_path} already exist")
        return base_path