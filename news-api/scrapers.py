from requests_html import HTMLSession


def get_page(url):
    s = HTMLSession()
    page = s.get(url).html
    s.close()
    return page


def get_content_bbcnews(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class='story-body'] div[property='articleBody'] p")
        if el.text is not None
    ])


def get_content_bussinessinsider(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[data-piano-inline-content-wrapper] p")
        if el.text is not None
    ])


def get_content_cnn(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[itemprop='articleBody'] [class^='zn-body__paragraph']")
        if el.text is not None
    ])


def get_content_thenewyorktimes(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in thenewyorktimes_page.find("section[name='articleBody'] p")
        if el.text is not None
    ])


def get_content_usatoday(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("article div[class='article-wrapper'] p")
        if el.text is not None
    ])


SCRAPER_DICT = {
    "bbc-news": get_content_bbcnews,
    "business-insider": get_content_bussinessinsider,
    "cnn": get_content_cnn,
    "the-new-york-times": get_content_thenewyorktimes,
    "usa-today": get_content_usatoday
}
