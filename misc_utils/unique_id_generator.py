#built-in imports
import datetime 
import re
import uuid
import time
import random


def unique_id_gen() -> str: 
    """Generates a random unique id based on time, day and a random float that is a valid filename as checked by regex
       Returns: 
       value (str) : the cleaned and valid filename (uuid)
    """
    value = "" 
    sha_time = str(time.time())
    sha_date_time = datetime.datetime.now().strftime("%b")
    cha_uuid_filename = uuid.uuid5(namespace=uuid.NAMESPACE_URL, name= str(sha_time + sha_date_time + str(random.random())))

    value = re.sub(r'[^\w\s-]', '', str(cha_uuid_filename).lower())
    value = re.sub(r'[-\s]+', '-', value).strip('-_')



    return str(value) 
