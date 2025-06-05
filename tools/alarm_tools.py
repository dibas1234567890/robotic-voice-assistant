#built-in imports
import dateparser
from langchain_core.tools import tool
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

@tool
def alarm_set_tool(alarm_time:str=None, alarm_date:str=None, alarm_duration:int=None)-> dict:
    """
    Set an alarm for a hotel room on the command.

    Args: 
        alarm_time(str): The time for the alarm.
        alarm_date(str): The date for the alarm.
        alarm_duration(int): Duration in hours from now to set the alarm.
    
    Returns: 
        dict: "status", "scheduled_time", "message" indicating the alarm is set or an error.
    
    
    """
    try:

        time_zone = ZoneInfo("Asia/Kathmandu")
        current_time = datetime.now(time_zone)

        time_string = f"{alarm_date or ''} {alarm_time or ''}".strip()
        scheduled_time = dateparser.parse(time_string)

        if alarm_duration is not None:
            if alarm_date or alarm_time:
                return "Error: Specify either a duration or a time/date for the alarm."
            scheduled_time = current_time + timedelta(hours=alarm_duration)
            return {

                    "status":"success",
                    "scheduled_time": scheduled_time.strftime('%Y-%m-%d %H:%M'),
                    "message": f"Alarm is set for {scheduled_time.strftime('%Y-%m-%d %H:%M')}."
  
                }
        
        if not alarm_time:
            return "Error: Please specify a time or use duration instead"

        if scheduled_time is None:
            return "Error:Could not understand the specified date or time for the alarm."
        
        if scheduled_time.tzinfo is None:
            scheduled_time = scheduled_time.replace(tzinfo=time_zone)

        scheduled_time = scheduled_time.astimezone(time_zone)

        if scheduled_time < current_time:
            scheduled_time += timedelta(days=1)

        return {

            "status":"success",
            "scheduled_time": scheduled_time.strftime('%Y-%m-%d %H:%M'),
            "message": f"Alarm is set for {scheduled_time.strftime('%Y-%m-%d %H:%M')}."

        }
    
    except Exception as e:
        return f"Error setting alarm:{str(e)}"
