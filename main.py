from scraper_wrapper import get_logger
from ReadWriteData import ScrapeData, out_file
from gui.search_gui import ShowData
from gui.warning_gui import AskToGetLatestData


if __name__ == "__main__":
    get_logger()

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

