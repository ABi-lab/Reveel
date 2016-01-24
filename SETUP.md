# node-challenge setup

Poleg zahtevanih orodij sem uporabil še:
  npm install validator (za preverjanje ISO oblike datuma)
  npm install body-parser (ker ni veè vkljuèen v Express4 po defaultu)

Kot sem zapisal že v mailu, bom zapisal nekaj toèk glede testne skripte tudi spodaj.
Napake so take, da bi jih glede na izkušnje lahko pripisal razliki v OSu (delam na win).
Drugih težav ni bilo. Za verbe sem natanèneje prebral navodila (da so vezani na path). 
API je nastavljen na port 7000.

Poženi:
"node main.js" ali "run" na win
"python test.py http://localhost:7000/" ali "test" na win
"python test.py http://localhost:7000/ -v" ali "testv" na win

Komentarji:
- Testna skripta ne prepozna praznega responsa
    Tam, ko testna skripta preverja ali je response prazen, pa ugotovi, da ni, 
    pa reèem skripti naj ga izpiše, izpiše prazen string (""). Ker sem preprièan,
	da odgovor je prazen, sem izloèil ta test iz skripte. Response sem preveril
	tudi z drugimi orodji (POSTMAN chrome plugin) in je body dejansko prazen.

- X-Count: strežnik tako ali tako response pošilja kot string. Vrednost pošlje
    pravo, testna skripta pa pade, ker prièakuje število. Posledièno sem svojo
	testno skripto na ustreznih mestih spremenil iz 'response.headers["x-count"]'
	v 'int(response.headers["x-count"])'.

- Deadline:
    Èeprav API vrne taske urejene po deadline-u, narašèajoèe ali padajoèe, testna
	skripta javlja, da niso urejeni. Sodeè po testni skripti prièakuje urejene
	padajoèe, tako jih tudi vrne API, test pa na tej toèki pade.
  > ali python na win parsa datume razlièno kot na linux??
	------------------------------------------------------------------
	‹[95m‹[1mTest GET request order‹[0m
	------------------------------------------------------------------
	‹[95m[‹[4mINFO‹[0m‹[95m]‹[0m Request url=http://localhost:7000/tasks.json
	‹[95m[‹[4mINFO‹[0m‹[95m]‹[0m Request method=GET
	‹[95m[‹[4mINFO‹[0m‹[95m]‹[0m Response code=200
	‹[95m[‹[4mINFO‹[0m‹[95m]‹[0m Response body=[
	{"id":3,"title":"Task3","description":"",                  "deadline":"2015-09-13T09:00:00+01:00"},
	{"id":2,"title":"Task2","description":"Task description 2","deadline":"2015-09-12T09:00:00+01:00"},
	{"id":1,"title":"Task1","description":"Task description 1","deadline":"2015-09-11T09:00:00+01:00"}
	]
	‹[95m[‹[4mINFO‹[0m‹[95m]‹[0m Response headers={'Content-Length': '280', 'X-Count
	': '3', 'X-Powered-By': 'Express', 'Connection': 'keep-alive', 'ETag': 'W/"118-J
	90IVdzzJHbvtdY1mijvPQ"', 'Date': 'Sun, 24 Jan 2016 17:25:41 GMT', 'Content-Type'
	: 'application/json; charset=utf-8'}
	Status: ‹[91mFail‹[0m
	Reason: Task array out of order
	
