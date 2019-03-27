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
        for el in page.find("div[itemprop='articleBody'] p, div[itemprop='articleBody'] h2")
        if el.text is not None])


def get_content_associatedpress(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class='Article'] p")
        if el.text is not None])


def get_content_axios(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class^='StoryBody'] div > ul, div[class^='StoryBody'] div > p")
        if el.text is not None])


def get_content_bbcnews(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class='story-body'] div[property='articleBody'] p")
        if el.text is not None])


def get_content_breitbartnews(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class='entry-content'] p, div[class='entry-content'] h2")
        if el.text is not None])


def get_content_bussinessinsider(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[data-piano-inline-content-wrapper] p")
        if el.text is not None])


def get_content_cbcnews(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class='story'] > span > p, div[class='story'] > span > h2")
        if el.text is not None])


def get_content_cnbc(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class='group'] p")
        if el.text is not None])


def get_content_cnn(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[itemprop='articleBody'] [class^='zn-body__paragraph']")
        if el.text is not None])


def get_content_dailymail(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[itemprop='articleBody'] p")
        if el.text is not None])


def get_content_engadget(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class^='article-text'] p")
        if el.text is not None])


def get_content_financialpost(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[itemprop='articleBody'] > p")
        if el.text is not None])


def get_content_foxnews(url):
    page = get_page(url)
    return " ".join([el.text
        for el in page.find("div[class='article-body'] > p")
        if el.text is not None and el.find("strong", first=True) is None])  # Pomijamy nagłówki innych artykułów wplecione w tekst -- są one pogrubiane


def get_content_independent(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class='body-content'] > p")[:-3]  # Wykluczamy ostatnie parę elementów, bo to śmieci, które są zwykle na końcu artykułu
        if el.text is not None])


def get_content_mashable(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("section[class^='article-content'] > p")
        if el.text is not None])


def get_content_mirror(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("div[class='article-body'] > p")
        if el.text is not None])


def get_content_thenewyorktimes(url):
    page = get_page(url)
    return " ".join([
        el.text
        for el in page.find("section[name='articleBody'] p")
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
    "axios": get_content_axios,
    "bbc-news": get_content_bbcnews,
    "breitbart-news": get_content_breitbartnews,
    "business-insider": get_content_bussinessinsider,
    "cbc-news": get_content_cbcnews,
    "cnbc": get_content_cnbc,
    "cnn": get_content_cnn,
    "daily-mail": get_content_dailymail,
    "engadget": get_content_engadget,
    "financial-post": get_content_financialpost,
    "fox-news": get_content_foxnews,
    "independent": get_content_independent,
    "mashable": get_content_mashable,
    "mirror": get_content_mirror,
    "the-new-york-times": get_content_thenewyorktimes,
    "usa-today": get_content_usatoday
}
