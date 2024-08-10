import os



COLOR_RED = "\e[31m"
COLOR_GREEN = "\e[32m"
COLOR_BLUE = "\e[34m"
COLOR_YELLOW = "\e[33m"
COLOR_VIOLET = "\e[35m"
COLOR_NONE = "\e[0m"
REDBGR='\033[0;41m'
NCBGR='\033[0m'

def logStage(message):
    os.system(f'echo "{COLOR_GREEN}-----{message}-----{COLOR_NONE}";')

def logNormal(message):
    os.system(f'echo "{COLOR_YELLOW}-----{message}-----{COLOR_NONE}";')

def logInfo(message):
    os.system(f'echo "{COLOR_BLUE}-----{message}-----{COLOR_NONE}";')

def logVio(message):
    os.system(f'echo "{COLOR_VIOLET}-----{message}-----{COLOR_NONE}";')
    
def logWarn(message):
    os.system(f'echo "{COLOR_RED}-----{message}-----{COLOR_NONE}";')
