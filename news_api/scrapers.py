from requests_html import HTMLSession


def get_page(url):
    s = HTMLSession()
    page = s.get(url).html
    s.close()
    return page


def get_content_bbc(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class='story-body'] div[property='articleBody'] p")
        if el.text is not None
    ])


def get_content_cnn(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[itemprop='articleBody'] [class^='zn-body__paragraph']")
        if el.text is not None
    ])


SCRAPER_DICT = {
    "bbc": get_content_bbc,
    "cnn": get_content_cnn
}
