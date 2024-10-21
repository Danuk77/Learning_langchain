import os
from dotenv import load_dotenv
from functools import cache

class Configuration:
    def __init__(self):
        pass
        
@cache
def get_configuration() -> Configuration:
    return Configuration()
