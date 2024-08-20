# JYSK_priceAlert
Program, ki sledi cenam izdelkov v JYSK spletni trgovini in jih beleži v excel datoteko. Ko cena pade pošlje e-mail s pomočjo Gmali API.

## Setup
 - Narediti moramo se datoteko config.json (glej config_example.json), v kateri definiramo:
    - TOKEN_PATH = pot do datoteke (datoteka se ustvari, ko se ob prvem poganjanju programa logiramo v gmail)
    - CREDENTIALS_PATH = pot do datoteke (dobimo v GCS- glej spodaj)
    - EXCEL_FILE = pot do excel datoteke
    - EMAIL_FROM = email s katerega se bo pošiljalo (definiran v GCS-glej spodaj)
    - EMAIL_TO = Email ki bo prejemal sporočilo
 - V Google Claud Service je potrebno narediti nov projekt in mu dodeliti Gmail API, potrebno je dodati dovoljenje za pošiljanje mailov
 - Pridobi se config.json 
 - Ob prvem zagonu se logiramo s mailom (mora biti na lisit razvijalcev v primeru zaprtega projekta), ko se logiramo se ustvari datoteka token.json.

## Samodejno izvajanje 
Če želimo, da se program (python skripta) izvaja dnevno, s pomočjo Task Scheduler:
1. "Create basic task" (v desnem zavihku)
2.  kot aplikacijo/skript se definira pot do python (najdes s `where python` v cmd)
3. kot argument se doda pot do skripte brez narekovajev
4. uporabno je da se obkljuka izvajanje programa tudi ko je uporabnik odjavljen

# Google Claud Service setup
## Pridobivanje credential.json
1. Naredi se nov projekt 
	1. Dropdown -> "New project"
	2. Poimenovanje
	3. Create
2. Omogočanje Gmail API
	1. "APIs & Services" > "Library"
	2.  Poišči in omogoči "GMAIL API"
3. OAuth 2.0 Credentials
	1. izpoli se vse kar se zahteva za aplikacijo
4. Naredi OAuth 2.0 Client ID
	1. "Credentials."
	2. "Create Credentials" -> "OAuth 2.0 Client ID."
	3. "Desktop App"
5. Downlowd .jason

## Dodeljevanje pravic za test user
Ko se bo prvič zagnala aplikacija se je potrebno prijaviti s gmail računom. Po tem se naredi datoteka "token.json", ko imamo to datoteko se ni več potrebno prijavljati. Če je aplikacija namenjena za interno uporabo (smo določili ko se je definrala aplikacija), je potrebno odobriti, račune ki imajo dostop do aplikacije:
1. "APIs & Services" > "OAuth consent screen"
2. "Test users"
3. doda se e-maile za avtorizacijo