
import sys
sys.path.insert(1, 'D:/codes/nb_cmd')
import nb_log
import time
logger = nb_log.get_logger(__name__)

for i in range(1000):
    logger.debug(f"debug: {i}")
    logger.info(f"info: {i}")
    logger.warning(f"warning: {i}")
    logger.error(f"error: {i}")
    logger.critical(f"critical: {i}")
    print(f"print: {i}")
    time.sleep(0.1)

"""

D:/ProgramData/Miniconda3/envs/py39b/python.exe D:/codes/nb_cmd/tests/ai_codes/print_many.py


"""