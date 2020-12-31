from icrawler.builtin import GoogleImageCrawler

filters = {
    'size': '>640x480',
    'type': 'photo',
}

keywords = (
    ('test_keyword1', 'test_category'),
    ('test_keyword2', 'test_category'),
)

def crawl_with_keyword(keyword):
    keyword, directory = keyword

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
        if pivot_date + date_delta > datetime.today():
            break
    
        keyword_filters = {
            'date': (pivot_date, pivot_date + date_delta),
        }

        google_crawler.crawl(
            keyword=keyword, 
            filters=filters, 
            keyword_filters=keyword_filters,
            max_num=15, 
            file_idx_offset='auto'
        )

if __name__ == '__main__':
    from multiprocessing import Pool

    with Pool(len(keywords)) as p:
        p.map(crawl_with_keyword, keywords)

