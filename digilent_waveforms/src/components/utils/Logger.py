import logging
from datetime import datetime

now = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

Logger = logging
logging_format = "[%(filename)s:%(lineno)s::%(funcName)s()] %(message)s"
Logger.basicConfig(
    level=logging.DEBUG,
    format=logging_format,
    handlers=[
        # logging.FileHandler(f"logs/digilent_waveforms-{now}.log"),
        logging.StreamHandler(),
    ],
)
