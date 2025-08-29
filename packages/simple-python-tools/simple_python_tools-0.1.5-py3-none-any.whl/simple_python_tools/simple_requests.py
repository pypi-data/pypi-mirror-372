import os
import time
import requests
from urllib.parse import quote

from . import simple_logger as logger

def get(url: str, headers = {}, payload = {}) -> requests.Response:
    logger.logger.debug(f'Try to get webpage from {url}')
    time.sleep(3)
    try:
        res = requests.get(url, headers = headers, params = payload)
    except KeyboardInterrupt:
        logger.warning("Program interrupted by user")
        return requests.Response()
    except Exception as e:
        logger.warning(e)
        return requests.Response()

    if res.status_code is None or res.status_code != 200:
        logger.warning("Downloading webpage failed", res.status_code)

    return res

def post(url: str, headers = {}, payload = {}) -> requests.Response:
    logger.debug(f'Try to get webpage from {url}')
    time.sleep(3)
    try:
        res = requests.post(url, headers=headers, data=payload)
    except KeyboardInterrupt:
        logger.warning("Program interrupted by user")
        return requests.Response()
    except Exception as e:
        logger.warning(e)
        return requests.Response()

    if res.status_code is None or res.status_code != 200:
        logger.warning("Downloading webpage failed", res.status_code)

    return res

def download(url, filename = '', location = ''):
    logger.debug(f'Try to download file from {url} to {filename} in {location}')
    if filename == '':
        filename = url.split('/')[-1].split('?')[0].split('#')[0]

    suffix = filename.split('.')[-1]
    name = filename.removesuffix('.' + suffix)
    filename = quote(name) + '.' + suffix
    
    if location != '':
        if not os.path.exists(location):
            os.makedirs(location)
        filename = os.path.join(location, filename)
    
    logger.info(f'Downloading file from {url} to {filename}')
    res = get(url)
    if res.status_code is None or res.status_code != 200:
        logger.warning(f"Failed to download file {filename}")
        return False

    with open(filename, 'wb') as f:
        f.write(res.content)

    logger.info(f"File {filename} downloaded")
    return True
