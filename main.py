from scraper_wrapper import get_logger
from ReadWriteData import ScrapeData, out_file
from gui.search_gui import ShowData
from gui.warning_gui import AskToGetLatestData



# def print_obj_data(obj):
#     logger.debug(f'User: {obj.user}\n')
#     # print(f'Time: {obj.time}')
#     logger.debug(f'url: {obj.url}\n')
#     logger.debug(f'Text: {obj.text}\n')

if __name__ == "__main__":
    get_logger()
    # out_file = Path('out/test_4gui.json')
    # out_file = Path('out/posts.json')

    if not out_file.is_file():
        ScrapeData()
    else:
        selection = AskToGetLatestData()
        if selection == 'Scrape Latest Posts':
            ScrapeData(get_again=True)
        if selection == 'Scrape Again':
            ScrapeData()
        if selection == 'Continue':
            pass
        else:
            exit(0)

    ShowData()

    # group_id = '753754635185088'
    # group_id = '165508793857687'
    # group_id = '399121444631603'

    # group_id = '1608483306030594'
    # group_id = '165508793857687'
    # group_id = '1389689534434104'
    # group_id = '2235042936775800'  # (خوشگوار ازدواجی زندگی کے راز) Happy Married Life
    # group_id = '181067471910524' # Study and life in germany

