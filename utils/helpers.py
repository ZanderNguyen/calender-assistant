from datetime import datetime

def contextualize_prompt(user_prompt):
    now = datetime.now()
    today = now.strftime("%A, %d %B %Y")
    current_time = now.strftime("%H:%M:%S") # might need to remove %S 
    return (
        f"Today is {today}, and the current time is {current_time}"
        f"Please extract all events from the following prompt with accurate start and end times in ISO 8601 format."
        f"{user_prompt}"
    )