from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException
from .scrapers import SCRAPER_DICT
import pandas as pd
import csv
import os
import math
import time


class NewsAPI:
    def __init__(self, token=None, sources=tuple(SCRAPER_DICT.keys())):
        """
        Konstruktor klasy NewsAPI. Tworzy nowy obiekt z polem za pomocą którego odpytujemy News API
        i listą źródeł, z których chcemy pozyskiwać artykuły.
        :param token: klucz uwierzytelniający
        :param sources: lista źródeł do wykorzystania (domyślnie: wszystkie obsługiwane)
        """
        assert isinstance(sources, tuple)
        assert len(sources) > 0

        # Jeśli nie podamy argumentu, to jest on odczytywany z pliku w którym powinien być sam klucz
        if token is None:
            assert os.path.isfile("news_api/token.txt")  # Plik powinen znajdować się w miejscu pozostałych plików
            with open("news_api/token.txt", "r") as token_file:
                token = token_file.readline().strip()

        self.api = NewsApiClient(api_key=token)
        self.articles_results = []
        self.sources = sources

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
            urls = set(pd.read_csv(csv_file).url)

            # Zdefiniowanie obiektu zapisującego
            writer = csv.DictWriter(csv_file, self.get_results(index).keys())

            # Zapisanie nagłówka
            if not csv_exists:
                writer.writeheader()

            # Pętla po zapisanych artykułach
            for article in self.get_results(index):
                if not article["url"] in urls:  # Sprawdzenie, czy artykuł nie jest duplikatem
                    urls.add(article["url"])    # Dodanie zapisanego adresu url do puli z którą weryfikujemy duplikaty
                    writer.writerow(article)    # Zapisanie artykułu

    def watch(self, csv_path, interval, keyword, **kwargs):
        """
        Funkcja, która co określony czas odpytuje API w poszukiwaniu artykułów o podanym słowie kluczowym.
        :param csv_path: ścieżka do wynikowego pliku csv (UWAGA: zakładamy, że nagłówek już jest w pliku)
        :param interval: czas oczekiwania między odpytaniami
        :param keyword: szukana fraza
        :param kwargs: pozostałe argumenty przekazywane do wrappera API
        """
        # Sprawdzenie, czy przy 1 stronie na interwał liczba odpytań się zepnie
        assert interval / math.ceil(len(self.sources)/20) > 1440*60 / 1000
        assert "from_param" not in kwargs.keys()  # Funkcja korzysta z tego parametrów
        assert "to" not in kwargs.keys()          # Funkcja korzysta z tego parametrów

        from_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())  # Aktualny czas
        try:
            # Co obrót pobiera dane z przedziału (from_time, to_time), który ma długość ~interwału
            while True:
                for i in range(interval):
                    print("Waiting... %02d" % (interval-i), end="\r")
                    time.sleep(1)

                print("%-13s" % "Working...")
                to_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                self.get_articles(keyword, from_param=from_time, to=to_time, **kwargs)
                self.save_to_csv(csv_path)
                self.clear_results()

                from_time = to_time

        except KeyboardInterrupt:
            print("My watch has ended.")

        except NewsAPIException as err:
            print(err)

    def get_past_month(self, csv_path, **kwargs):
        pass
