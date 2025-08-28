from datetime import datetime

def validate_date(date: str, format_str: str):
    """
    Validate whether date string is in appropriate datetime format
    """
    try: 
        datetime.strptime(date, format_str)
        return True
    except ValueError:
        return False
