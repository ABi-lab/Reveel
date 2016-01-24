# node-challenge setup

Poleg zahtevanih orodij sem uporabil �e:
  npm install validator (za preverjanje ISO oblike datuma)
  npm install body-parser (ker ni ve� vklju�en v Express4 po defaultu)

Kot sem zapisal �e v mailu, bom zapisal nekaj to�k glede testne skripte tudi spodaj.
Napake so take, da bi jih glede na izku�nje lahko pripisal razliki v OSu (delam na win).
Drugih te�av ni bilo. Za verbe sem natan�neje prebral navodila (da so vezani na path). 
API je nastavljen na port 7000.

Po�eni:
"node main.js" ali "run" na win
"python test.py http://localhost:7000/" ali "test" na win
"python test.py http://localhost:7000/ -v" ali "testv" na win

Komentarji:
- Testna skripta ne prepozna praznega responsa
    Tam, ko testna skripta preverja ali je response prazen, pa ugotovi, da ni, 
    pa re�em skripti naj ga izpi�e, izpi�e prazen string (""). Ker sem prepri�an,
	da odgovor je prazen, sem izlo�il ta test iz skripte. Response sem preveril
	tudi z drugimi orodji (POSTMAN chrome plugin) in je body dejansko prazen.

- X-Count: stre�nik tako ali tako response po�ilja kot string. Vrednost po�lje
    pravo, testna skripta pa pade, ker pri�akuje �tevilo. Posledi�no sem svojo
	testno skripto na ustreznih mestih spremenil iz 'response.headers["x-count"]'
	v 'int(response.headers["x-count"])'.

- Deadline:
    �eprav API vrne taske urejene po deadline-u, nara��ajo�e ali padajo�e, testna
	skripta javlja, da niso urejeni. Sode� po testni skripti pri�akuje urejene
	padajo�e, tako jih tudi vrne API, test pa na tej to�ki pade.
  > ali python na win parsa datume razli�no kot na linux??
	------------------------------------------------------------------
	�[95m�[1mTest GET request order�[0m
	------------------------------------------------------------------
	�[95m[�[4mINFO�[0m�[95m]�[0m Request url=http://localhost:7000/tasks.json
	�[95m[�[4mINFO�[0m�[95m]�[0m Request method=GET
	�[95m[�[4mINFO�[0m�[95m]�[0m Response code=200
	�[95m[�[4mINFO�[0m�[95m]�[0m Response body=[
	{"id":3,"title":"Task3","description":"",                  "deadline":"2015-09-13T09:00:00+01:00"},
	{"id":2,"title":"Task2","description":"Task description 2","deadline":"2015-09-12T09:00:00+01:00"},
	{"id":1,"title":"Task1","description":"Task description 1","deadline":"2015-09-11T09:00:00+01:00"}
	]
	�[95m[�[4mINFO�[0m�[95m]�[0m Response headers={'Content-Length': '280', 'X-Count
	': '3', 'X-Powered-By': 'Express', 'Connection': 'keep-alive', 'ETag': 'W/"118-J
	90IVdzzJHbvtdY1mijvPQ"', 'Date': 'Sun, 24 Jan 2016 17:25:41 GMT', 'Content-Type'
	: 'application/json; charset=utf-8'}
	Status: �[91mFail�[0m
	Reason: Task array out of order
	
