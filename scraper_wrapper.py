import os
import time
from pathlib import Path

from scrapper import utils
from scrapper.entry import *


log_file = Path(__file__).resolve().parent / 'out/parser_log.log'

def get_logger():
    if not log_file.parent.is_dir():
        os.mkdir(log_file.parent)
    utils.enable_logging(log_file)

def get_posts_data(group_id, cookies_file, pages_to_read, latest_date, max_past_limit):
    start_url = None
    def handle_pagination_url(url):
        logger.debug(url)
        global start_url
        start_url = url

    while True:
        try:
            posts = get_posts(group=group_id, start_url=start_url,
                              request_url_callback=handle_pagination_url,
                              cookies=cookies_file,
                              options={"comments": True}, pages=pages_to_read,
                              latest_date=latest_date, max_past_limit=max_past_limit)
            break
        except exceptions.TemporarilyBanned:
            logger.debug("Temporarily banned, sleeping for 5m")
            time.sleep(300)
    return posts

