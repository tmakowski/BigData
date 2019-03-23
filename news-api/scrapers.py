from requests_html import HTMLSession


def get_page(url):
    s = HTMLSession()
    page = s.get(url).html
    s.close()
    return page


def get_content_abcnews(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[id='articleBody'] p")
        if el.text is not None])


def get_content_abcnewsau(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class='article section'] p")
        if el.text is not None])


def get_content_aljazeeraenglish(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class='article-p-wrapper'] p")
        if el.text is not None])


def get_content_arstechnica(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[itemprop='articleBody'] p,h2")
        if el.text is not None])


def get_content_associatedpress(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class='Article'] p")
        if el.text is not None])


def get_content_bbcnews(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class='story-body'] div[property='articleBody'] p")
        if el.text is not None])


def get_content_bussinessinsider(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[data-piano-inline-content-wrapper] p")
        if el.text is not None])


def get_content_cnn(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[itemprop='articleBody'] [class^='zn-body__paragraph']")
        if el.text is not None])


def get_content_foxnews(url):
    page = get_page(url)
    return " ".join([el.text
        for el in page.find("div[class='article-body'] > p")
        if el.text is not None and el.find("strong", first=True) is None])  # Pomijamy nagłówki innych artykułów wplecione w tekst -- są one pogrubiane


def get_content_thenewyorktimes(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in thenewyorktimes_page.find("section[name='articleBody'] p")
        if el.text is not None])


def get_content_usatoday(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("article div[class='article-wrapper'] p")
        if el.text is not None])


SCRAPER_DICT = {
    "abc-news": get_content_abcnews,
    "abc-news-au": get_content_abcnewsau,
    "al-jazeera-english": get_content_aljazeeraenglish,
    "ars-technica": get_content_arstechnica,
    "associated-press": get_content_associatedpress,
    "bbc-news": get_content_bbcnews,
    "business-insider": get_content_bussinessinsider,
    "cnn": get_content_cnn,
    "fox-news": get_content_foxnews,
    "the-new-york-times": get_content_thenewyorktimes,
    "usa-today": get_content_usatoday
}
