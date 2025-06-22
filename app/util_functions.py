from datetime import datetime, timedelta
import random
import pytz
import uuid

def get_current_time():
    india_timezone = pytz.timezone("Asia/Kolkata")
    dt = datetime.now(india_timezone)
    return dt.replace(tzinfo=None)  # removes timezone info

def get_add_delta_to_current_time(days=3):
    return get_current_time() + timedelta(days=days)

def get_add_delta_to_current_time_for_session(minutes=3):
    return get_current_time() + timedelta(minutes=minutes)

def compare_with_current_time(dt_to_compare):
    current_time = get_current_time()  # this returns a timezone-aware datetime in Asia/Kolkata

    if current_time.tzinfo is None or current_time.tzinfo.utcoffset(current_time) is None:
        india_timezone = pytz.timezone("Asia/Kolkata")
        current_time = india_timezone.localize(current_time)
    else:
        # Convert any other tz-aware datetime to IST
        current_time = current_time.astimezone(pytz.timezone("Asia/Kolkata"))

    # If dt_to_compare is naive, localize it to Asia/Kolkata
    if dt_to_compare.tzinfo is None or dt_to_compare.tzinfo.utcoffset(dt_to_compare) is None:
        india_timezone = pytz.timezone("Asia/Kolkata")
        dt_to_compare = india_timezone.localize(dt_to_compare)
    else:
        # Convert any other tz-aware datetime to IST
        dt_to_compare = dt_to_compare.astimezone(pytz.timezone("Asia/Kolkata"))


    if dt_to_compare < current_time:
        return "Past"
    elif dt_to_compare > current_time:
        return "Future"
    else:
        return "Present"


def is_over_due(dt_to_compare):
    res = compare_with_current_time(dt_to_compare)
    if res == "Future":
        return False
    return True

def still_has_time(dt_to_compare):
    return not is_over_due(dt_to_compare)

def generate_string():
    return str(uuid.uuid4())[:8]

def generate_otp(length=6):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def generate_username(role):
    role = role.strip().lower()  # Normalize input

    # Role to type mapping
    if role in ['intern', 'trainee']:
        user_type = 'I'
    elif role in ['coe', 'cto', 'cfo', 'chro', 'dod', 'dot', 'dos']:
        user_type = 'A'
    elif role in ['user', 'client']:
        user_type = 'U'
    elif role in ['employee', 'staff']:
        user_type = 'E'
    elif role == 'owner':
        user_type = 'O'
    else:
        raise ValueError(f"Invalid role: {role}")

    # Fetch or create the sequence row
    from app.models import UserNameGenerationSequence
    sequence = UserNameGenerationSequence.query.filter_by(type=user_type).first()
    if not sequence:
        return None

    # Generate the username
    username = sequence.generate_username()

    return username

