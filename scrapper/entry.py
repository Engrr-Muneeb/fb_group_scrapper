import logging
import warnings
import pickle
from typing import Any, Dict, Iterator, Optional, Set, Union

from requests.cookies import cookiejar_from_dict

from .constants import DEFAULT_REQUESTS_TIMEOUT, DEFAULT_COOKIES_FILE_PATH
from .facebook_scraper import FacebookScraper
from .fb_types import Credentials, Post, Profile
from .utils import parse_cookie_file, enable_logging, logger
from . import exceptions

_scraper = FacebookScraper()


def set_cookies(cookies):
    if isinstance(cookies, str):
        if cookies == "from_browser":
            try:
                import browser_cookie3

                cookies = browser_cookie3.load(domain_name='.facebook.com')
            except:
                raise ModuleNotFoundError(
                    "browser_cookie3 must be installed to use browser cookies"
                )
        else:
            try:
                cookies = parse_cookie_file(cookies)
            except ValueError as e:
                raise exceptions.InvalidCookies(f"Cookies are in an invalid format: {e}")
    elif isinstance(cookies, dict):
        cookies = cookiejar_from_dict(cookies)
    if cookies is not None:
        cookie_names = [c.name for c in cookies]
        missing_cookies = [c for c in ['c_user', 'xs'] if c not in cookie_names]
        if missing_cookies:
            raise exceptions.InvalidCookies(f"Missing cookies with name(s): {missing_cookies}")
        _scraper.session.cookies.update(cookies)
        if not _scraper.is_logged_in():
            raise exceptions.InvalidCookies(f"Cookies are not valid")


def unset_cookies():
    # Explicitly unset cookies to return to unauthenticated requests
    _scraper.session.cookies = cookiejar_from_dict({})


def set_proxy(proxy, verify=True):
    _scraper.set_proxy(proxy, verify)


def set_user_agent(user_agent):
    _scraper.set_user_agent(user_agent)


def set_noscript(noscript):
    _scraper.set_noscript(noscript)


def get_profile(
    account: str,
    **kwargs,
) -> Profile:
    """Get a Facebook user's profile information
    Args:
        account(str): The account of the profile.
        cookies (Union[dict, CookieJar, str]): Cookie jar to use.
            Can also be a filename to load the cookies from a file (Netscape format).
    """
    _scraper.requests_kwargs['timeout'] = kwargs.pop('timeout', DEFAULT_REQUESTS_TIMEOUT)
    cookies = kwargs.pop('cookies', None)
    set_cookies(cookies)
    return _scraper.get_profile(account, **kwargs)


def get_reactors(
    post_id: Union[str, int],
    **kwargs,
) -> Iterator[dict]:
    """Get reactors for a given post ID
    Args:
        post_id(str): The post ID, as returned from get_posts
        cookies (Union[dict, CookieJar, str]): Cookie jar to use.
            Can also be a filename to load the cookies from a file (Netscape format).
    """
    _scraper.requests_kwargs['timeout'] = kwargs.pop('timeout', DEFAULT_REQUESTS_TIMEOUT)
    cookies = kwargs.pop('cookies', None)
    set_cookies(cookies)
    return _scraper.get_reactors(post_id, **kwargs)


def get_page_info(account: str, **kwargs) -> Profile:
    """Get a page's information
    Args:
        account(str): The account of the profile.
        cookies (Union[dict, CookieJar, str]): Cookie jar to use.
            Can also be a filename to load the cookies from a file (Netscape format).
    """
    _scraper.requests_kwargs['timeout'] = kwargs.pop('timeout', DEFAULT_REQUESTS_TIMEOUT)
    cookies = kwargs.pop('cookies', None)
    set_cookies(cookies)
    return _scraper.get_page_info(account, **kwargs)


def get_group_info(group: Union[str, int], **kwargs) -> Profile:
    """Get a group's profile information
    Args:
        group(str or int): The group name or ID
        cookies (Union[dict, CookieJar, str]): Cookie jar to use.
            Can also be a filename to load the cookies from a file (Netscape format).
    """
    _scraper.requests_kwargs['timeout'] = kwargs.pop('timeout', DEFAULT_REQUESTS_TIMEOUT)
    cookies = kwargs.pop('cookies', None)
    set_cookies(cookies)
    return _scraper.get_group_info(group, **kwargs)


def get_posts(
    account: Optional[str] = None,
    group: Union[str, int, None] = None,
    post_urls: Optional[Iterator[str]] = None,
    hashtag: Optional[str] = None,
    credentials: Optional[Credentials] = None,
    **kwargs,
) -> Iterator[Post]:
    """Get posts from a Facebook page or group.

    Args:
        account (str): The account of the page.
        group (int): The group id.
        post_urls ([str]): List of manually specified post URLs.
        credentials (Optional[Tuple[str, str]]): Tuple of email and password to login before scraping.
        timeout (int): Timeout for requests.
        page_limit (int): How many pages of posts to go through.
            Use None to try to get all of them.
        extra_info (bool): Set to True to try to get reactions.
        youtube_dl (bool): Use Youtube-DL for video extraction.
        cookies (Union[dict, CookieJar, str]): Cookie jar to use.
            Can also be a filename to load the cookies from a file (Netscape format).

    Yields:
        dict: The post representation in a dictionary.
    """
    valid_args = sum(arg is not None for arg in (account, group, post_urls, hashtag))

    if valid_args != 1:
        raise ValueError("You need to specify either account, group, or post_urls")

    _scraper.requests_kwargs['timeout'] = kwargs.pop('timeout', DEFAULT_REQUESTS_TIMEOUT)

    cookies = kwargs.pop('cookies', None)

    if cookies is not None and credentials is not None:
        raise ValueError("Can't use cookies and credentials arguments at the same time")
    set_cookies(cookies)

    options: Union[Dict[str, Any], Set[str]] = kwargs.setdefault('options', {})
    if isinstance(options, set):
        warnings.warn("The options argument should be a dictionary.", stacklevel=2)
        options = {k: True for k in options}
    options.setdefault('account', account)

    # TODO: Add a better throttling mechanism
    if 'sleep' in kwargs:
        warnings.warn(
            "The sleep parameter has been removed, it won't have any effect.", stacklevel=2
        )
        kwargs.pop('sleep')

    # TODO: Deprecate `pages` in favor of `page_limit` since it is less confusing
    if 'pages' in kwargs:
        kwargs['page_limit'] = kwargs.pop('pages')

    # TODO: Deprecate `extra_info` in favor of `options`
    if "reactions" not in options:
        options['reactions'] = kwargs.pop('extra_info', False)
    options['youtube_dl'] = kwargs.pop('youtube_dl', False)

    if credentials is not None:
        _scraper.login(*credentials)

    if account is not None:
        return _scraper.get_posts(account, **kwargs)

    elif group is not None:
        return _scraper.get_group_posts(group, **kwargs)

    elif hashtag is not None:
        return _scraper.get_posts_by_hashtag(hashtag, **kwargs)

    elif post_urls is not None:
        return _scraper.get_posts_by_url(post_urls, **kwargs)

    raise ValueError('No account nor group')


def get_posts_by_search(
    word: str,
    credentials: Optional[Credentials] = None,
    **kwargs,
) -> Iterator[Post]:
    """Get posts by searching all of Facebook
    Args:
        word (str): The word for searching posts.
        credentials (Optional[Tuple[str, str]]): Tuple of email and password to login before scraping.
        timeout (int): Timeout for requests.
        page_limit (int): How many pages of posts to go through.
            Use None to try to get all of them.
        extra_info (bool): Set to True to try to get reactions.
        youtube_dl (bool): Use Youtube-DL for video extraction.
        cookies (Union[dict, CookieJar, str]): Cookie jar to use.
            Can also be a filename to load the cookies from a file (Netscape format).

    Yields:
        dict: The post representation in a dictionary.
    """
    if not word:
        raise ValueError("You need to specify word")

    _scraper.requests_kwargs['timeout'] = kwargs.pop('timeout', DEFAULT_REQUESTS_TIMEOUT)

    cookies = kwargs.pop('cookies', None)

    if cookies is not None and credentials is not None:
        raise ValueError("Can't use cookies and credentials arguments at the same time")
    set_cookies(cookies)

    options: Union[Dict[str, Any], Set[str]] = kwargs.setdefault('options', {})
    if isinstance(options, set):
        warnings.warn("The options argument should be a dictionary.", stacklevel=2)
        options = {k: True for k in options}

    options.setdefault('word', word)

    # TODO: Add a better throttling mechanism
    if 'sleep' in kwargs:
        warnings.warn(
            "The sleep parameter has been removed, it won't have any effect.", stacklevel=2
        )
        kwargs.pop('sleep')

    # TODO: Deprecate `pages` in favor of `page_limit` since it is less confusing
    if 'pages' in kwargs:
        kwargs['page_limit'] = kwargs.pop('pages')

    # TODO: Deprecate `extra_info` in favor of `options`
    if "reactions" not in options:
        options['reactions'] = kwargs.pop('extra_info', False)
    options['youtube_dl'] = kwargs.pop('youtube_dl', False)

    if credentials is not None:
        _scraper.login(*credentials)

    if word is not None:
        return _scraper.get_posts_by_search(word, **kwargs)

    raise ValueError('No account nor group')


def get_groups_by_search(
    word: str,
    **kwargs,
):
    """Searches Facebook groups and yields ids for each result
    on the first page"""
    _scraper.requests_kwargs['timeout'] = kwargs.pop('timeout', DEFAULT_REQUESTS_TIMEOUT)
    cookies = kwargs.pop('cookies', None)
    set_cookies(cookies)
    return _scraper.get_groups_by_search(word, **kwargs)



def use_persistent_session(email: str, password: str, cookies_file_path=DEFAULT_COOKIES_FILE_PATH):
    """Login persistently to Facebook and save cookies to a file (default: ".fb-cookies.pckl"). This is highly recommended if you want to scrape several times a day because it will keep your session alive instead of logging in every time (which can be flagged as suspicious by Facebook).

    Args:
        email (str): email address to login.
        password (str): password to login.
        cookies_file_path (str, optional): path to the file in which to save cookies. Defaults to ".fb-cookies.pckl".

    Raises:
        exceptions.InvalidCredentials: if the credentials are invalid.

    Returns:
        Boolean: True if the login was successful, False otherwise.
    """
    try:
        with open(cookies_file_path, "rb") as f:
            cookies = pickle.load(f)
        logger.debug("Loaded cookies from %s", cookies_file_path)
    except FileNotFoundError:
        logger.error("No cookies file found at %s", cookies_file_path)
        cookies = None
    try:
        if not cookies:
            raise exceptions.InvalidCookies()
        set_cookies(cookies)
        logger.debug("Successfully logged in with cookies")
    except exceptions.InvalidCookies:
        logger.exception("Invalid cookies, trying to login with credentials")
        _scraper.login(email, password)
        cookies = _scraper.session.cookies
        with open(cookies_file_path, "wb") as f:
            pickle.dump(cookies, f)
        set_cookies(cookies)
        logger.debug("Successfully logged in with credentials")
