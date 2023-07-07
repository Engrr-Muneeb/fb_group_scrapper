
import shutil
import os
from datetime import datetime
import time
import json
from pathlib import Path

from scraper_wrapper import get_posts_data, logger, log_file
from gui.initial_gui import CreateInitGUI, DEFAULT_COOKIES_FILE_PATH
from gui.gui_loging import redirect_stdout, end_scraping
from data_types import FBPost, Comment, Reply


out_file = Path(__file__).resolve().parent / 'out/posts.json'
inp_file_name = out_file.parent / "inp_params"

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

def ScrapeData(get_again=False):

    if not get_again:
        user_inputs = AskUserInputs()
        cookies_file = str(user_inputs["cookies_file"])
        group_id = user_inputs["group_id"]
        number_of_pages = user_inputs["number_of_pages"]
        date = user_inputs["selected_date"]
    else:
        group_id, number_of_pages, date = ReadInputFile()
        cookies_file = str(DEFAULT_COOKIES_FILE_PATH)

    log_window_handle, log_window = redirect_stdout(log_file, logger)
    logger.debug('Scraping Data.....')
    logger.debug(f'Group ID: {group_id}')
    logger.debug(f'Pages to Scrape: {number_of_pages}')
    logger.debug(f'Date: {date}')
    time.sleep(1)

    ParseAndWriteData(group_id=group_id, cookies_file=cookies_file,
                      pages_to_read=number_of_pages,
                      latest_date=date, get_again=get_again)

    end_scraping(logger, log_window_handle, log_window)


def ParseAndWriteData(group_id, cookies_file, pages_to_read, latest_date, get_again):
    max_limit = 3
    if get_again:
        max_limit = 1

    WriteInputFile(group_id, pages_to_read, latest_date)
    posts = get_posts_data(group_id, cookies_file,
                           pages_to_read, latest_date,
                           max_past_limit=max_limit)

    if get_again:
        old_posts = GetDataFromOutFile()
        posts = list(posts)
        posts.extend(old_posts)

    with open(out_file, 'w') as fid:
        json.dump(list(posts), fid, indent=4, sort_keys=True, default=str)


def GetDataFromOutFile():
    with open(out_file, "r") as in_:  
        # Reading from file
        posts = json.loads(in_.read())
    return posts

def ReadDataFromFile(filters):
    post_list =list()

    posts = GetDataFromOutFile()

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
            post_obj.AddComments(post_comments)
            post_list.append(post_obj)
        # break
    return post_list


def WriteInputFile(group_id, pages_to_read, latest_date):
    with open(inp_file_name, 'w') as out_:
        out_.write(f"{str(time.time())}\n")
        out_.write(f"group_id:{group_id}\n")
        out_.write(f"pages_to_read:{pages_to_read}\n")
        out_.write(f"latest_date:{latest_date}\n")


def ReadInputFile():
    in_ = open(inp_file_name).readlines()
    last_time = datetime.fromtimestamp(float(in_[0].strip()))
    group_id = in_[1].split(':')[-1].strip()
    pages_to_read = int(in_[2].split(':')[-1].strip())
    return group_id, pages_to_read, last_time
