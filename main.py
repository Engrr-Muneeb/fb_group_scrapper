from pathlib import Path

from scraper_wrapper import get_logger, logger
from filter_class import Filters
from ReadWriteData import ScrapeData, ReadDataFromFile


def print_obj_data(obj):
    logger.debug(f'User: {obj.user}\n')
    # print(f'Time: {obj.time}')
    logger.debug(f'url: {obj.url}\n')
    logger.debug(f'Text: {obj.text}\n')

if __name__ == "__main__":
    log_file = Path('out/parser_log.log')
    get_logger(log_file)

    out_file = Path('out/posts.json')
    # out_file = Path('out/test_4gui.json')
    # out_file = Path('out/posts.json')

    if not out_file.is_file():
        ScrapeData(log_file, out_file)

    # string_to_search = "That's completely normal"

    # Public groups
    # group_id = '753754635185088'
    # group_id = '165508793857687'
    # group_id = '399121444631603'

    # group_id = '1608483306030594'
    # group_id = '165508793857687'
    # group_id = '1389689534434104'
    # group_id = '2235042936775800'  # (خوشگوار ازدواجی زندگی کے راز) Happy Married Life
    # group_id = '181067471910524' # Study and life in germany
    # cookies_file = "cookies.txt"
    # cookies_file = "um_cookies.txt"
    # group_name = get_group_info(group_id, cookies=cookies_file)['name']

    # if not out_file.is_file():
    #     ParseAndWriteData(group_id=group_id, cookies_file=cookies_file,
    #                       out_file=out_file, pages_to_read=pages,
    #                       latest_date=date)

    # string_to_search = "applied"
    # include_users = ['Eshaal Sohail', 'Muhammad Faiq']

    #TODO: Add GUI for search and filters
    string_to_search = ""
    include_users = []
    exclude_users = []
    
    filters = Filters(string_to_search=string_to_search, include_users=include_users, exclude_users=exclude_users)

    posts = ReadDataFromFile(out_file=out_file, filters=filters)
    logger.debug(f'matched posts:{len(posts)}')

    for post_obj in posts:
        logger.debug('\n\n POST:: \n')
        print_obj_data(post_obj)
        for comment in post_obj.comments:
            print_obj_data(comment)
            logger.debug(f'parent_post:{comment.post}')
            for reply in comment.replies:
                print_obj_data(reply)
                logger.debug(f'parent_comment:{reply.comment}')
