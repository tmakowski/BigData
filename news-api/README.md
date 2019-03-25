# News API

Klasa `NewsAPI` jest gotowa i dość szczegółowo opisana, więc zrozumienie co tam się dzieje nie powinno być problemem. Główna metoda to `watch`, która na bieżąco pobiera info z api na temat podanego słowa kluczowego.

Obsługiwane serwisy (gotowe scrapery): status jest w pliku `scrapers_todo.csv`

**UWAGA:** trzeba uważać na kodowanie w wynikowych csv-kach.

## Przykład wykorzystania

1. Umieścić token w pliku `token.txt`
1. Zaimportować klasę `NewsApi` i stworzyć nowy obiekt:
```
from NewsApi import NewsApi
api = NewsApi()
```
1. Uruchomienie jednej z dwóch opcji, to jest: `api.watch(<results_csv_path>, <interval>, <keyword>)` albo `api.get_past_month(<results_csv_path, <keyword>)`, gdzie `<keyword>` to szukana fraza, a `<interval>` to czas pauzy w sekundach pomiędzy pobraniem danych.