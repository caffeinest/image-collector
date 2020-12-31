from icrawler.builtin import GoogleImageCrawler

keywords = (
    ('test_keyword', 'test_category'),
)

keyword, directory = keywords[0]

google_crawler = GoogleImageCrawler(
    feeder_threads=1,
    parser_threads=1,
    downloader_threads=2,
    storage={'root_dir': './data/' + directory},
)

start_date = datetime(year=2010, month=1, day=1)
date_delta = timedelta(days=120)

for i in range(10000000):
    pivot_date = start_date + date_delta * i
    keyword_filters = {
        'date': (pivot_date, pivot_date + date_delta),
    }

    google_crawler.crawl(
        keyword=keyword,
        filters=filters,
        keyword_filters=keyword_filters,
        max_num=15,
    )
