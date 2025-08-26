from datetime import datetime, time


class Validator:
    @staticmethod
    def validate_digit(value):
        try:
            if float(value):
                return True
        except:
            return False

    @staticmethod
    def validate_int(value):
        return isinstance(value, int) and value != 0

    @staticmethod
    def validate_float(value):
        return isinstance(value, float) and value != 0.00

    @staticmethod
    def validate_string_not_null(value):
        return isinstance(value, str) and value != ""

    @staticmethod
    def validate_bool(value):
        return isinstance(value, bool) and value is not None

    @staticmethod
    def validate_date_format(date_string):
        if date_string is None or date_string == "":
            return False

        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_time_range(start_time_str, end_time_str):
        try:
            # Convert time strings to datetime objects for comparison
            start_time = datetime.strptime(start_time_str, "%H:%M")
            end_time = datetime.strptime(end_time_str, "%H:%M")

            # Check if start_time is equal to end_time
            if start_time == end_time:
                return False  # Time range is invalid

            # Check if end_time is greater than start_time
            if end_time > start_time:
                return True  # Time range is valid

            return False  # Time range is invalid
        except ValueError:
            return False  # Invalid time format

    @staticmethod
    def validate_date_time_range(start_time_str, end_time_str):
        try:
            # Convert time strings to datetime objects for comparison
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M')

            # Check if start_time is equal to end_time
            if start_time == end_time:
                return False  # Time range is invalid

            # Check if end_time is greater than start_time
            if end_time > start_time:
                return True  # Time range is valid

            return False  # Time range is invalid
        except ValueError:
            return False  # Invalid time format

    @staticmethod
    def validate_date_range(start_date_str, end_date_str):
        try:
            # Convert time strings to datetime objects for comparison
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

            # Check if end_time is greater than start_time
            if end_date > start_date or start_date == end_date:
                return True  # Time range is valid

            return False  # Time range is invalid
        except ValueError:
            return False  # Invalid time format

    @staticmethod
    def validate_dates(date_values, target_date):
        current_date = [datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d') for date_str in
                        date_values]
        target_date = datetime.strptime(target_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        matching_dates = [date for date in current_date if date == target_date]

        return matching_dates

    @staticmethod
    def is_same_date(date):
        # Parse the given date string into a datetime object
        given_date = datetime.strptime(date, '%Y-%m-%d')

        # Get the current date
        current_date = datetime.now()

        # Compare the two dates (ignoring time)
        return given_date.date() == current_date.date()

    @staticmethod
    def is_time_within_range(input_time):

        # Define the start and end times
        start_time = time(8, 0)  # 08:00 AM
        end_time = time(17, 0)  # 05:00 PM

        # Parse the input time as a datetime object
        input_datetime = datetime.strptime(input_time, '%H:%M')

        # Extract the time from the datetime object
        input_time = input_datetime.time()

        # Check if the input time is within the specified range
        return start_time <= input_time <= end_time

    @staticmethod
    def is_duration_greater_than_one_hour(start_time, end_time):
        # Parse start and end times
        start = datetime.strptime(start_time, '%H:%M')
        end = datetime.strptime(end_time, '%H:%M')

        # Calculate the duration
        duration = end - start

        # Check if the duration is greater than or equal to 1 hour (3600 seconds)
        return duration.total_seconds() >= 3600

    @staticmethod
    def validate_start_date(start_date_str):
        # Convert the start_date_str to a datetime object
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

        # Get the current date
        current_date = datetime.now()
        formatted_date_str = current_date.strftime("%Y-%m-%d")
        formatted_date = datetime.strptime(formatted_date_str, "%Y-%m-%d")

        # Compare the start_date with the current date
        if start_date >= formatted_date:
            return True
        else:
            return False
