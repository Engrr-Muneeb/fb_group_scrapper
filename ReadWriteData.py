
import shutil
import os
from datetime import datetime
import time
import sys
import json

from scraper_wrapper import get_posts_data, logger
from gui.initial_gui import CreateInitGUI, DEFAULT_COOKIES_FILE_PATH
from gui.gui_loging import redirect_stdout, end_scraping
from data_types import FBPost, Comment, Reply


def get_comment_data(comment):
    name = comment['commenter_name']
    comment_text = comment['comment_text']
    comment_url = comment['comment_url']
    comment_time = comment['comment_time']
    return name, comment_text, comment_url, comment_time

def CopyCookiesFile(user_inputs):
    cookies_file = user_inputs["cookies_file"]
    if not DEFAULT_COOKIES_FILE_PATH.parent.is_dir():
        os.mkdir(DEFAULT_COOKIES_FILE_PATH.parent)
    if DEFAULT_COOKIES_FILE_PATH != cookies_file:
        shutil.copy(cookies_file, DEFAULT_COOKIES_FILE_PATH)
    user_inputs['cookies_file'] = DEFAULT_COOKIES_FILE_PATH

def AskUserInputs():
    user_inputs = CreateInitGUI()
    CopyCookiesFile(user_inputs)
    selected_date = user_inputs["selected_date"]
    stamp = time.mktime(datetime.strptime(selected_date, "%d-%m-%Y").timetuple())
    date = datetime.fromtimestamp(stamp)
    user_inputs["selected_date"] = date
    return user_inputs

def ScrapeData(log_file, out_file):
    user_inputs = AskUserInputs()
    cookies_file = str(user_inputs["cookies_file"])
    group_id = user_inputs["group_id"]
    number_of_pages = user_inputs["number_of_pages"]
    date = user_inputs["selected_date"]

    log_window_handle = redirect_stdout(log_file, logger)
    logger.debug('Scraping Data.....')
    logger.debug(f'Group ID: {group_id}')
    logger.debug(f'Pages to Scrape: {number_of_pages}')
    logger.debug(f'Date: {date}')
    time.sleep(1)

    ParseAndWriteData(group_id=group_id, cookies_file=cookies_file,
                      out_file=out_file, pages_to_read=number_of_pages,
                      latest_date=date)

    end_scraping(logger, log_window_handle)


def ParseAndWriteData(group_id, cookies_file, out_file, pages_to_read, latest_date):

    posts = get_posts_data(group_id, cookies_file, out_file, pages_to_read, latest_date)

    with open(out_file, 'w') as fid:
        json.dump(list(posts), fid, indent=4, sort_keys=True, default=str)

def ReadDataFromFile(out_file, filters):
    post_list =list()

    with open(out_file, "r") as in_:  
        # Reading from file
        posts = json.loads(in_.read())

    for post in posts:
        is_text_matched = list()
        post_comments = []
        # out.write(f"{str(post)}\n")
        text = post['text']
        is_text_matched.append(filters.MatchText(text))
        post_time = post['time']
        post_url = post['post_url']
        user_name = post['username']
        all_comments = list(post['comments_full'])

        out_ = open('out/out_pposts.txt', 'w', encoding="UTF-8")
        out_.write(f"POST:\n{str(post)}\n\n")

        if not filters.IncludeUser(user_name) or filters.ExcludeUser(user_name):
            continue

        post_obj = FBPost(user=user_name, url=post_url, text=text, time= post_time)

        for comment in all_comments:
            # print('Comment')
            # exit()
            name, comment_text, comment_url, comment_time = get_comment_data(comment)
            is_text_matched.append(filters.MatchText(comment_text))
            comment_obj = Comment(user=name, url=comment_url, time=comment_time, text=comment_text)
            comment_obj.SetParentPost(post_obj)
            post_comments.append(comment_obj)
            replies = list(comment['replies'])
            if replies:
                for reply in replies:
                    name, comment_text, comment_url, comment_time = get_comment_data(reply)
                    is_text_matched.append(filters.MatchText(comment_text))
                    reply_obj = Reply(user=name, url=comment_url, time=comment_time, text=comment_text)
                    reply_obj.SetParentComment(comment_obj)
                    comment_obj.AddReply(reply_obj)

        if any(is_text_matched):
            out_.write("\nMATCHED\n")
            post_obj.AddComments(post_comments)
            post_list.append(post_obj)
        # break
    return post_list