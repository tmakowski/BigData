from datetime import datetime, timedelta
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException
from requests.exceptions import RequestException
from scrapers import SCRAPER_DICT
from time import sleep
import pandas as pd
import csv
import os
import math


class NewsApi:
    def __init__(self, token=None, sources=tuple(SCRAPER_DICT.keys()), keep_blanks=True):
        """
        Konstruktor klasy NewsAPI. Tworzy nowy obiekt z polem za pomocą którego odpytujemy News API
        i listą źródeł, z których chcemy pozyskiwać artykuły.
        :param token: klucz uwierzytelniający
        :param sources: lista źródeł do wykorzystania (domyślnie: wszystkie obsługiwane)
        :param keep_blanks: flaga, czy zapisywać tytuły i info artykułach bez treści do pliku (źle zescrapowane etc.)
        """
        assert isinstance(sources, tuple)
        assert len(sources) > 0
        assert isinstance(keep_blanks, bool)

        # Jeśli nie podamy argumentu, to jest on odczytywany z pliku w którym powinien być sam klucz
        if token is None:
            assert os.path.isfile("token.txt")  # Plik powinen znajdować się w miejscu pozostałych plików
            with open("token.txt", "r") as token_file:
                token = token_file.readline().strip()

        self.api = NewsApiClient(api_key=token)
        self.articles_results = []
        self.sources = sources
        self.keep_blanks = keep_blanks

    def clear_results(self):
        """
        Funkcja czyści poprzednio zapisane wyniki artykułów.
        """
        self.articles_results = []
        return self

    def get_results(self, index):
        """
        Funkcja zwraca wyniki danego wyszukiwania.
        :param index: które wyszukiwanie ma zostać zwrócone (0 to najstarsze)
        :return: wyniki wyszukiwania
        """
        assert isinstance(index, int)
        assert -len(self.articles_results) <= index < len(self.articles_results)

        return self.articles_results[index]

    def get_articles(self, keyword, **kwargs):
        """
        Funkcja zwraca wszystkie artykuły związane z podanym słowem kluczowym.
        :param keyword: słowo kluczowe, którego szukamy
        :param kwargs: dodatkowe parametry przekazywane do API
        :return: zaktualizowany obiekt NewsAPI o wyniki z wyszukiwania
        """
        assert isinstance(keyword, str)
        assert "page" not in kwargs.keys()       # Funkcja manipuluje tym argumentem
        assert "page_size" not in kwargs.keys()  # Ustawiony na sztywno na maksymalną wartość
        assert "language" not in kwargs.keys()   # Tylko angielski

        # Inicjalizacja zmiennych do pętli
        i = 0
        n = len(self.sources)
        articles = []

        # Odpytywanie po maksymalnie 20 źródeł na raz, bo takie ograniczenie ma News API
        while 20 * i < n:
            current_sources = ",".join(self.sources[i:min(20 * (i + 1) - 1, n)])

            # Odpytywanie dopóki nie skończą się strony z wynikami
            page_nr = 1
            while True:
                current_response = self.api.get_everything(
                    q=keyword,
                    page=page_nr,
                    sources=current_sources,
                    language="en",
                    **kwargs
                )
                articles += current_response.get("articles")

                page_nr += 1
                # Sprawdzenie, czy przekroczyliśmy liczbę istniejących wyników, bądź limit stron (10) dla naszego API
                if 100 * page_nr >= min(current_response["totalResults"], 1001):
                    break
            i += 1

        # Formatowanie wyników
        results = [
            {
                "source_id":  art.get("source").get("id"),
                "date":       art.get("publishedAt"),
                "url":        art.get("url"),
                "title":      art.get("title"),
                "content":    SCRAPER_DICT[art.get("source").get("id")](art.get("url"))
            } for art in articles
            if art.get("source").get("id") in SCRAPER_DICT.keys()
        ]

        # Zapisanie wyników
        self.articles_results.append(results)
        return self

    def save_to_csv(self, csv_path, index=-1):
        """
        Funkcja zapisuje wyniki spod podanego indeksu do wskazanego pliku csv. Jeśli plik nie istnieje,
        to będzie stworzony i z początku zostanie zapisany nagłówek.
        :param csv_path: ścieżka wynikowej csv do której zapisujemy dane
        :param index: który wynik zapisać (domyślnie: ostatni wyszukiwany)
        """
        csv_exists = os.path.isfile(csv_path)
        with open(csv_path, "a", encoding="utf-8") as csv_file:
            urls = set(pd.read_csv(csv_path).url) if csv_exists else set()

            # Zdefiniowanie obiektu zapisującego
            writer = csv.DictWriter(csv_file, fieldnames=("source_id", "date", "url", "title", "content"))

            # Zapisanie nagłówka
            if not csv_exists:
                writer.writeheader()

            # Pętla po zapisanych artykułach
            for article in self.get_results(index):
                # Sprawdzenie, czy artykuł nie jest duplikatem i czy zapisywać, jeśli nie ma treści
                if not article["url"] in urls and (self.keep_blanks or article["content"] != ""):
                    urls.add(article["url"])    # Dodanie zapisanego adresu url do puli z którą weryfikujemy duplikaty
                    writer.writerow(article)    # Zapisanie artykułu

    def watch(self, csv_path, interval, keyword, **kwargs):
        """
        Funkcja, która co określony czas odpytuje API w poszukiwaniu artykułów o podanym słowie kluczowym.
        :param csv_path: ścieżka do wynikowego pliku csv
        :param interval: czas oczekiwania między odpytaniami
        :param keyword: szukana fraza
        :param kwargs: pozostałe argumenty przekazywane do wrappera API
        """
        # Sprawdzenie, czy przy 1 stronie na interwał liczba odpytań się zepnie
        assert interval / math.ceil(len(self.sources)/20) > 1440*60 / 500
        assert "from_param" not in kwargs.keys()  # Funkcja korzysta z tego parametru
        assert "to" not in kwargs.keys()          # Funkcja korzysta z tego parametru

        from_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")  # Aktualny czas
        
        # Co obrót pobiera dane z przedziału (from_time, to_time), który ma długość równą wartości interwału
        while True:
            try:
                for i in range(interval):
                    print("\rWaiting... %03d" % (interval-i), end="")
                    sleep(1)

                print("\r%-13s" % "Working...", end="")
                to_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                self.get_articles(keyword, from_param=from_time, to=to_time, **kwargs)
                if self.get_results(-1) != list():
                    self.save_to_csv(csv_path)
                self.clear_results()

                from_time = to_time

#            except NewsAPIException as err:  # Błędy najpewniej spowodowane problemami z połączeniem
#                print(err)
#                continue
                    
#            except RequestException:  # Jeśli zdarzy się jakiś błąd z siecią, to po prostu ponawiamy próbę w kolejnej iteracji
#                continue

            except KeyboardInterrupt:
                print("\nMy watch has ended.")
            
            # Przy jakimkolwiek błędzie przechodzimy dalej, czyli odczekamy kolejną minutę i wtedy odpytamy Api
            # Kolejne odpytanie po błędzie będzie z dłuższego okresu, ponieważ parametr `from_time` się nie zmieni -- tym samym nie ominiemy żadnego artykułu
            except:
                pass

    def get_past_month(self, csv_path, keyword, **kwargs):
        """
        Funkcja zapisuje artykuły z ostatnich 28 dni do pliku csv.
        :param csv_path: ścieżka do wynikowego pliku csv
        :param keyword: szukana fraza
        :param kwargs: pozostałe argumenty przekazywane do wrappera API
        """
        assert "from_param" not in kwargs.keys()  # Funkcja korzysta z tego parametru
        assert "to" not in kwargs.keys()          # Funkcja korzysta z tego parametru

        current_time = datetime.utcnow()

        for days_back in range(1, 29):
            curr_day = (current_time - timedelta(days=days_back)).strftime("%Y-%m-%d")
            self.get_articles(keyword, from_param=curr_day, to=curr_day, **kwargs)
            self.save_to_csv(csv_path)
            self.clear_results()
