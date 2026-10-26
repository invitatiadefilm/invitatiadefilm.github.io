# Pagini de invitație pentru clienți

1. Copiază `clienti/irina-mihai.json` în `clienti/<slug>.json` (slug: ex. `ana-victor-2027`) și completează datele.
   - `tip`: `nunta`, `botez` sau `aniversare` (textele implicite se schimbă singure; oricare se poate suprascrie în JSON).
   - `video`, `poster`, `og`: linkurile clipului clientului (og = imagine 1200x630 pentru previzualizarea pe WhatsApp; dacă lipsește se folosește posterul).
   - `rsvp.cazare`: textul bifei de cazare sau lipsă (fără cazare). `rsvp.meniuri`: lista de meniuri sau `[]`.
2. `python3 unelte/genereaza.py unelte/clienti/<slug>.json`, apoi commit + push.
3. În tabelul Google „Confirmari”, foaia **Evenimente**, adaugă un rând: `<slug>` | `COD` (ex. AV2027). Foaia cu răspunsuri se creează singură la prima confirmare.
4. Clientul primește: linkul invitației `https://invitatiadefilm.github.io/<slug>/` (pentru invitați) și linkul `.../<slug>/raspunsuri/` + codul (doar pentru el).

Codul nu se scrie niciodată în repo (repo-ul e public).
