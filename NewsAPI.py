from newsapi import NewsApiClient


class NewsAPI:
    def __init__(self, token, sources = None):
        """
        token   -- klucz uwierzytelniający
        sources -- opcjonalna lista id źródeł zgodna z konwencją News API
        """
        self.api = NewsApiClient(api_key = token)
        self.articles_results = []
        self.urls_results = []
        self.content_results = []
        
        if sources is None:
            self.set_sources_all()
        else:
            assert isinstance(sources, list)
            self.sources = sources
            
    def clear_results(self):
        """ Metoda czyści zapisane wyniki. """
        self.articles_results = []
        self.urls_results = []
        self.content_results = []
        return self
    
    
    def get_results(self, index = -1):
        """ Metoda zwraca wybrane wyniki. Można podać `slice()` jako argument. """
        return self.articles_results[index], self.urls_results[index]#, self.content_results[index]
    
    
    def set_sources_all(self):
        """ Metoda ustawia pole `sources` na wszystkie dostępne źródła angielskojęzyczne. """
        self.sources = [src["id"] for src in self.api.get_sources(language="en")["sources"]]
        return self
    
    
    def __get_all_articles(self, keyword, **kwargs):
        """ keyword -- wyszukiwana fraza, kwargs -- argumenty przekazywane to api """    
        assert isinstance(self.sources, list)
        
        i = 0
        n = len(self.sources)
        articles = []
        
        while 20*i < n:
            curr_response = self.api.get_everything(
                q       = keyword,
                sources = ",".join(self.sources[i:min(20*(i+1)-1, n)]),  # Przetwarzamy 20 na raz, bo takie ograniczenie ma News API
                **kwargs)
            articles += curr_response.get("articles")
            i += 1
        
        self.articles_results.append(articles)
        return self
    
    
    def __dict_urls_by_source(self):
        """ Metoda upakowuje adresy artykułów do słownika według id źródeł. """
        urls_by_source = {}
        
        for art in self.articles_results[-1]:
            curr_source_id = art.get("source").get("id")
            
            # Dodanie klucza, jeśli go nie ma
            if curr_source_id not in urls_by_source.keys():
                urls_by_source[curr_source_id] = []
            
            urls_by_source[curr_source_id].append(art.get("url"))
            urls_by_source[curr_source_id] = list(set(urls_by_source[curr_source_id]))  # żeby uniknąć duplikatów
        
        self.urls_results.append(urls_by_source)
        return self
    
    
    def __scrape_urls(self):
        # Scraper po id źródła
        pass
    
    
    def process(self, keyword, **kwargs):
        self.__get_all_articles(keyword, **kwargs)
        self.__dict_urls_by_source()
        #self.__scrape_urls()
        
        return self.get_results()    
        