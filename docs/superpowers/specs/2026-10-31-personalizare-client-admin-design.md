# Kitcraft: personalizarea pe cont de client, design

**Data:** 2026-10-31
**Status:** înlocuit pe 2026-11-05 de `2026-11-05-kitcraft-client-admin-inspector-design.md`. Rămâne doar ca istoric. A fost aprobat de Tudor pe 2026-10-31.
**Sursa:** propunerile profesoarei de licență, aduse de Tudor pe 31 octombrie
2026, și brainstormingul din aceeași zi.

---

## 1 · Pe înțeles

Aplicația face ce face un croitor bun. Clientul vine cu o idee și câteva poze.
Croitorul îl întreabă ce nu e clar, îi face o schiță, iar clientul o aprobă
sau cere schimbări. La final croitorul verifică haina cusută față de schița
aprobată.

Azi aplicația face doar ultimii pași, și doar pentru operator: transformă o
descriere în specificații și verifică poza produsului față de ele. Designul
ăsta adaugă primii pași, făcuți chiar de client în contul lui: descrierea,
întrebările, schița generată și aprobarea. Și extinde produsul de la tricou la
un set de piese cu aceeași identitate: tricou, hanorac, geacă, șapcă, șosete,
pantaloni.

**Cât de greu e de explicat:** conturile, formularul și piesele noi sunt
ușoare, pentru că sunt aceleași idei ca în aplicațiile web obișnuite. Partea
grea e una singură: imaginea separată a tricoului trebuie să arate exact ca
tricoul din imaginea completă. Soluția e explicată în 6.3.

## 2 · De ce

Profesoara de licență a aprobat cele patru module din 16 octombrie 2026 și a
cerut să se adauge:

- generarea unei imagini pe baza descrierii, pentru un echipament complet;
- o parte de admin și una de client: clientul completează cererea în aplicație,
  pe profilul lui, și primește un model generat, iar adminul preia cererile de
  acolo;
- ca direcție de dezvoltare și scalabilitate, extinderea la un echipament
  complet, nu doar la tricouri.

Ce o face valoroasă pentru licență: lanțul se închide. Descrierea clientului
devine un model aprobat, modelul aprobat devine referința cu care Image Match
compară produsul real, iar verificarea de la final se face față de ce a aprobat
clientul, nu față de ce și-a imaginat operatorul.

## 3 · Obiective

1. Două tipuri de cont: **client** și **admin**.
2. Clientul face o **cerere**: alege piesele din catalog, descrie setul cu
   vorbele lui și poate încărca sigla și poze de referință.
3. Înainte de generare, aplicația îi pune **clientului** întrebările de
   clarificare.
4. Se generează **o imagine cu setul complet**, cu toate piesele alese
   împreună, și **câte o imagine pentru fiecare piesă**.
5. Clientul **aprobă** modelul sau **cere modificări** în cuvinte, iar modelul
   se reface pornind de la imaginea precedentă.
6. Adminul vede **toate cererile, din ambele surse**, adică formularul și
   emailul, cu specificațiile pe fiecare piesă, și rulează verificările.
7. Imaginea aprobată a fiecărei piese devine **referința pentru Image Match**.
8. **Catalogul are șase piese**, iar o piesă nouă se adaugă doar cu o schemă
   nouă, fără cod. Ăsta e argumentul de scalabilitate cerut de profesoară.
9. **Fluxul A, Discovery plus Inspector, rămâne funcțional**, la fel ca azi.
   **Emailul rămâne** sursă de cereri.

## 4 · Non-obiective

Lucruri care nu se fac, ca să nu crească proiectul:

- nume și numere personalizate pe fiecare purtător;
- mărimi, cantități, prețuri, ofertare, plăți;
- găzduire publică: aplicația rămâne locală, pe laptop;
- resetarea parolei pe email, autentificarea în doi pași, logarea cu Google;
- notificări pe email către client;
- clientul nu vede rapoartele de verificare; ele sunt ale adminului.

## 5 · Anti-obiective

Situații în care proiectul a eșuat, chiar dacă tehnic rulează:

- **Piesele nu seamănă cu setul.** Dacă tricoul din imaginea lui are altă
  nuanță sau sigla în alt loc decât în imaginea completă, Image Match
  verifică produsul față de o referință greșită și tot lanțul își pierde
  sensul.
- **Generarea inventează.** Sigla deformată, text greșit pe produs, elemente
  pe care clientul nu le-a cerut.
- **Se strică ce merge azi.** Fluxul A, Image Match, emailul sau cele 168 de
  teste existente. Fixture-ul comun al testelor poate intra logat ca admin,
  vezi 8.9, dar verificările din teste nu se schimbă.
- **Factura vine neanunțată.** Consum peste creditele lunare fără ca Tudor să
  știe.
- **O piesă nouă cere cod.** Atunci argumentul de scalabilitate cade.

## 6 · Ce a hotărât Tudor

Toate pe 31 octombrie 2026.

### 6.1 · Fluxul cererii

- Cererea intră pe două căi: **formularul clientului**, nou, și **emailul**,
  care rămâne.
- Clientul își completează cererea în contul lui și primește modelul generat.
- Întrebările de clarificare le primește **clientul**, înainte de generare.
  Motivul lui Tudor: așa se preia direct ce vrea clientul.
- Clientul **aprobă** modelul sau **cere modificări**.
- Din contul de admin, Tudor extrage specificațiile și face verificările.
- Clientul poate încărca **poze de referință** în timpul descrierii.
- **O modificare cerută de client actualizează și specificațiile, nu doar
  imaginea.** Motivul: altfel Inspector, care verifică produsul față de
  specificații, și Image Match, care îl verifică față de imaginea aprobată, s-ar
  contrazice pe același produs.

### 6.2 · Produsul

- Cazul principal e **merch-ul unui brand**. Echipamentul de fotbal e doar o
  situație dintre multe.
- Piesele depind de cerere: clientul alege din **tricou, hanorac, geacă,
  șapcă, șosete, pantaloni**.

### 6.3 · Imaginile

- O imagine cu **setul complet**, pentru client.
- **Câte o imagine pe piesă**, pentru Image Match. Motivul: poza produsului
  real e de obicei cu o singură piesă.
- Imaginea aprobată a fiecărei piese devine **referința pentru Image Match**.

### 6.4 · Furnizorul de imagini

- **Google, Gemini API, modelul `gemini-nano-banana-2.1`**, plătit din cei 10
  dolari pe lună de credite Google Cloud incluși în abonamentul Google AI Pro
  al lui Tudor. Asta înseamnă cam 300 de imagini pe lună, la 1K.
- Alegerea s-a făcut după research-ul din 31 octombrie 2026. OpenAI
  `gpt-image-2.5-sunburst` e primul în clasamentul Arena la editarea cu mai
  multe imagini, cu 1521 de puncte pe 26 octombrie, dar costă bani separat de
  ChatGPT. Nano Banana 2.1 e al cincilea, cu 1432, și poate ieși gratuit. Tudor
  a ales varianta gratuită.

### 6.5 · Numele

Aplicația se va numi **Kitcraft**, de la setul de piese făcut pe comandă,
în locul lui „Ciptronic Product Validator”. Tudor a ales numele pe 31
octombrie 2026, dintr-o listă de propuneri. Numele se schimbă în aplicație și
în lucrare, nu și pe disc: folderul și repo-ul rămân `ciptronic-validator`,
pentru că mutarea lor ar rupe căile și venv-ul. *Partea despre disc e alegerea
lui Claude.*

### 6.6 · Locul în roadmap

Propunerile profesoarei intră **primele**, în locul contractelor din ianuarie
2027. Restul modulelor se mută după ele. Ce nu încape până pe 1 mai se
hotărăște în februarie, cum era deja stabilit.

## 7 · Cum arată

Schițele din brainstorming sunt în AIS-OS, în
`.superpowers\brainstorm\1612-1793449020\content\`: `drum-cerere.html` pentru
drum și cele două ecrane, `client-model-v2.html` pentru pașii clientului. Sunt
schițe de discuție, nu design vizual final.

### 7.1 · Clientul

1. **Contul.** Clientul își face singur cont, cu email, parolă și numele
   brandului. *Alegerea lui Claude.*
2. **Cerere nouă.** Alege piesele din catalog, cel puțin una, iar fiecare
   piesă apare cel mult o dată într-o cerere. Două tricouri diferite înseamnă
   două cereri. *Alegerea lui Claude.* Scrie descrierea. Încarcă opțional sigla și până la 6 poze de referință.
   *Numărul de poze e alegerea lui Claude:* Nano Banana 2.1 primește până la
   10 imagini de obiect pe cerere, iar restul locurilor rămân pentru sigla și
   imaginea completă, la generarea pieselor.
3. **Întrebările.** Discovery îi pune clientului întrebări, în maximum 5
   runde **pentru toată cererea**, nu 5 pe fiecare piesă, cu cel mult 8
   întrebări pe rundă. Întrebările pot privi orice piesă și se grupează pe
   teme. Discovery vede și pozele de referință, ca să nu întrebe ce se vede
   deja în ele. *Toate trei sunt alegerea lui Claude.*
4. **Ce a rămas necompletat.** Dacă după ultima rundă mai sunt câmpuri goale,
   clientul primește un formular scurt doar cu ele, cu variante de ales acolo
   unde schema le are. Generarea pornește abia când specificația fiecărei
   piese e completă. Aplicația nu completează nimic din burtă. *Alegerea lui
   Claude.*
5. **Modelul setului.** Aplicația generează imaginea completă, cu toate
   piesele alese.
6. **Aprob sau cer modificări, pe imaginea completă.** La „cer modificări”,
   clientul scrie ce vrea schimbat, de exemplu „fă hanoracul negru”. Întâi un
   pas cu Claude schimbă în specificații câmpurile atinse de modificare, apoi
   imaginea se reface pornind de la cea precedentă, nu de la zero. Unele
   modificări nu au câmp în specificații, cum e „dungile mai late”; pe acelea
   le poartă doar imaginea, iar Image Match le verifică. Sunt permise **cel mult
   5 runde de modificări pe cerere**, ca să rămână în credite. *Limita e
   alegerea lui Claude.*
7. **Piesele, după aprobare.** Abia după ce clientul aprobă setul, aplicația
   face imaginile pe piese, o singură dată, din imaginea completă aprobată.
   Clientul le vede, dar nu le mai aprobă separat. Dacă o piesă nu seamănă cu
   setul, adminul o poate reface, de cel mult 2 ori pe piesă. *Alegerea lui
   Claude:* așa, o rundă de modificări costă o imagine, nu șapte, iar piesele
   pornesc toate de la aceeași imagine aprobată. O cerere cu șase piese
   consumă cel mult 6 imagini de set, 6 de piese și 12 refaceri.
8. **Cererile mele.** Lista cererilor lui, fiecare cu starea: în descriere,
   model de aprobat, aprobat, piese gata.

### 7.2 · Adminul

1. **Contul.** Unul singur, al lui Tudor, creat la instalare, nu prin
   înregistrare publică. *Alegerea lui Claude.*
2. **Lista cererilor.** Toate cererile, din ambele surse, cu sursa, clientul,
   piesele și starea.
3. **Cererea deschisă.** Descrierea, sigla, pozele de referință, întrebările
   și răspunsurile, specificațiile fiecărei piese, imaginea completă și
   imaginile pe piese, cu cea aprobată marcată. Specificațiile se pot descărca
   pe fiecare piesă. *Descărcarea e alegerea lui Claude.*
4. **Verificările, pe fiecare piesă:**
   - **Fluxul A**, Inspector: adminul încarcă poza produsului real, iar
     Inspector o compară cu specificațiile piesei, pe trei zone: conform,
     neconform, nevizibil. Exact ca azi.
   - **Fluxul B**, Image Match: imaginea aprobată a piesei e referința.
     Adminul încarcă doar poza produsului real și primește raportul criteriu cu
     criteriu.
5. **Cererile din email.** Apar în aceeași listă, cu sursa „email”. Fiecare
   produs extras dintr-un email devine o cerere separată, cu o singură piesă,
   la fel cum azi fiecare produs are butonul lui. Întrebările de clarificare
   i le pune adminului, ca azi, pentru că clientul nu e în aplicație. Adminul
   poate genera modelul și îl aprobă el, ca să aibă referința pentru Image
   Match. *Alegerea lui Claude.*

### 7.3 · Fluxul A și paginile de azi

Paginile de azi, `/sessions/new` și cele care urmează, `/matches/new` și
verificarea emailului, rămân și se comportă la fel. Pentru că acum există
conturi, ele aparțin adminului: un client logat nu ajunge la ele. *Alegerea lui
Claude.*

O singură schimbare la pagina de email: butonul de azi, „creează sesiune”, de
la `/email-agent/create-session`, înregistrează acum și cererea, cu sursa
„email”. Verificarea emailurilor tot nu salvează nimic singură. Cererea se ține
minte după emailul și poziția produsului în el, așa că o a doua apăsare deschide
cererea existentă, nu una dublă. Nu apare un al doilea buton. *Alegerea lui
Claude.*

## 8 · Cum se leagă de cod

Codul de azi: FastAPI, HTMX, Jinja2, SQLite, Claude Sonnet 4.6 prin
`agents\llm_client.py`. Regulile din `CLAUDE.md`-ul proiectului rămân, cu o
excepție, la 8.6.

### 8.1 · Piesele

- Cinci scheme noi în `schemas\`, în același format ca `tricou.json`:
  hanorac, geacă, șapcă, șosete, pantaloni.
- Câmpurile fiecărei scheme le scrie builderul după modelul tricoului.
- Regula rămâne: **o piesă nouă înseamnă doar `schemas\<nume>.json`**. Asta
  include generarea de imagini. Promptul de generare se construiește generic
  din câmpurile schemei, nu are text scris pe fiecare piesă.
- Schemele pot primi **chei opționale noi**, inclusiv `tricou.json`. Cheile
  spun dacă un câmp se vede într-o poză, cum nu se văd materialul sau tehnica,
  și dacă un câmp vine din identitatea comună a setului, cum vin culorile și
  sigla. Codul care nu le cunoaște le ignoră. Numele cheilor sunt ale
  builderului. *Alegerea lui Claude.*

### 8.2 · Cererea cu mai multe piese

- Constrângerea: **la final, fiecare piesă are propria specificație completă,
  în exact formatul de azi**, adică o sesiune Discovery cu `product_type` egal
  cu piesa. Așa Inspector, raportul și paginile de azi merg fără schimbări.
- Cum se poartă conversația pentru toată cererea, în maximum 5 runde, se lasă
  la builder: fie o schemă compusă din piese, desfăcută la final pe piese, fie
  sesiuni pe piese cu întrebările adunate într-o singură rundă. Atenție:
  `schemas\loader.py` știe azi un singur nivel de imbricare.
- O piesă se identifică în cerere prin `product_type`, pentru că apare cel
  mult o dată, vezi 7.1.
- Pentru cererile clientului, specificația trebuie să fie completă înainte de
  generare, vezi 7.1, pasul 4. Pentru sesiunile de azi ale operatorului,
  comportamentul rămâne: după 5 runde sesiunea se închide chiar dacă e
  incompletă.
- Identitatea comună a setului, adică brandul, culorile, sigla și stilul, stă
  la nivel de cerere, nu se repetă pe fiecare piesă.

### 8.3 · Generarea imaginilor

- Un modul nou, de exemplu `image_gen\`, cu o singură interfață publică de
  trei operații:
  1. **setul complet**: din identitate, specificațiile pieselor, siglă și
     pozele de referință;
  2. **piesa**: din imaginea completă aprobată, plus specificația piesei și
     sigla;
  3. **modificarea**: din imaginea completă precedentă și instrucțiunea
     clientului. Înainte de ea, specificațiile pieselor se actualizează cu
     ce atinge instrucțiunea, vezi 7.1, pasul 6. Pasul ăsta e text, cu
     Claude prin `agents\llm_client.py`, nu cu generatorul de imagini.
- **Imaginea fiecărei piese se face din imaginea completă, folosită ca
  referință**, nu separat din text. Asta e soluția pentru consistență: modelul
  primește setul deja desenat și i se cere să izoleze piesa, cu aceleași
  culori și aceeași siglă în același loc. *Alegerea lui Claude.*
- Piesele se generează pe fundal uniform, alb sau transparent, ca referința
  pentru Image Match să fie curată. *Alegerea lui Claude.*
- Furnizorul stă **într-un singur fișier**. Schimbarea pe OpenAI înseamnă un
  fișier nou și o setare, nu modificări prin aplicație.
- Prompturile de generare stau în `.md`, în `prompts\`, după regula de azi.
- Cheia stă în `.env`, ca `GEMINI_API_KEY`, și nu se comite niciodată.
- Rezoluția implicită e 1K. Mai mare doar dacă evals arată că 1K nu ajunge
  pentru Image Match.

### 8.4 · Legătura cu Image Match

Imaginea aprobată a piesei se salvează și se dă ca `sim` lui `analyze_sim`,
exact ca un mockup încărcat azi la `/matches`. Motorul din `image_matcher\` nu
se schimbă și rămâne standalone.

### 8.5 · Emailul

`email_extractor` alege deja `product_type` din `available_product_types()`,
deci piesele noi sunt recunoscute automat din emailuri. Fiecare produs extras
rămâne o cerere separată, cu o singură piesă, ca azi. Așa, două tricouri
diferite din același email nu se ciocnesc. *Alegerea lui Claude.* Cum se
înregistrează cererea e descris în 7.3.

### 8.6 · Conturile, și regula care se schimbă

- Regula de azi, „single-user, fără auth, deliberat”, se înlocuiește cu: **două
  roluri, client și admin, tot local**. Regula „nu expune serverul pe rețea fără
  protecție” rămâne.
- Parolele se stochează doar ca hash, cu o bibliotecă standard. Sesiunea stă
  într-un cookie.
- Încărcările de imagini au aceleași limite ca azi: 5 MB și verificarea
  tipului. Un client vede doar cererile și imaginile lui.
- `CLAUDE.md`-ul proiectului se actualizează cu regula nouă.

### 8.7 · Baza de date

Doar tabele noi, pentru utilizatori, cereri, piesele cererii, încărcări și
imagini generate. Tabelele de azi, `discovery_sessions`, `validation_reports`
și `match_sessions`, rămân neschimbate. Structura exactă e a builderului.

### 8.8 · Bugetul de imagini

- Aplicația numără imaginile generate și le arată adminului pe luna curentă.
- **Plafon lunar în aplicație**, setabil, implicit 280 de imagini, adică cam
  9,4 dolari la 1K. La plafon, generarea se oprește cu un mesaj clar, pentru
  client și pentru admin. Plafonul contează pentru că clienții își fac singuri
  cont. *Alegerea lui Claude.*
- Limitele de la 7.1 se aplică pe cerere.
- În Google Cloud se pune o alertă de buget la 10 dolari, ca depășirea să nu
  vină neanunțată. Alerta doar anunță, nu oprește; oprirea o face plafonul.
- **Nicio cheltuială peste credite fără acordul explicit al lui Tudor.** Dacă
  creditele din AI Pro nu se activează, înainte de orice trecere pe OpenAI se
  revine la Tudor cu costul estimat. *Alegerea lui Claude.*

### 8.9 · Testele

- Testele unitare și e2e folosesc un generator fals, la fel cum azi
  `get_llm_client` e înlocuit în teste. Nu cheamă API-ul.
- Testele care cheamă Gemini real stau separat, ca `tests\integration` azi.
- Cele 168 de teste existente trec în continuare. Fixture-ul comun `client`
  din `tests\conftest.py` poate intra logat ca admin, dar verificările din
  teste nu se schimbă. *Alegerea lui Claude.*
- Teste noi verifică faptul că un vizitator nelogat și un client nu ajung la
  paginile adminului, iar un client nu vede cererile altui client.

## 9 · Evals

Regula din roadmap: un modul e gata abia când are evals. Aici sunt trei,
fiecare rulat de mai multe ori pe un set de 10–20 de cereri de test:

1. **Fidelitatea față de specificații.** Imaginea fiecărei piese trece prin
   **Inspector**, adică prin Fluxul A, ca și cum ar fi poza produsului.
   Fluxul A devine astfel și instrumentul de măsură al generării. O piesă
   trece dacă nu are niciun câmp neconform și dacă fiecare câmp care se vede
   într-o poză iese conform. Câmpurile care nu se văd, cum sunt materialul și
   tehnica, pot ieși „nevizibil”. Pragul pentru modul: cel puțin 80% din piese
   trec, la fiecare dintre 3 rulări. *Pragul e alegerea lui Claude* și se
   revede după prima rulare.
2. **Consistența piesă–set.** Imaginea piesei se compară cu imaginea completă:
   culori, poziția siglei, elemente. Builderul alege între a refolosi Image
   Match, cu imaginea piesei ca referință și cea completă ca „produs”, sau un
   judecător separat cu Claude vision.
3. **Sigla.** Sigla încărcată apare pe piesele pe care trebuie, nedeformată și
   neinversată. `image_matcher` are deja verificarea siglelor în oglindă.

Fiecare rulare consumă credite. Setul de evals trebuie să încapă într-o lună de
credite, alături de dezvoltare.

## 10 · Ce rămâne la builder

- mecanismul conversației pentru toată cererea, din 8.2;
- câmpurile celor cinci scheme noi;
- structura tabelelor;
- biblioteca de hash și de sesiune;
- textul prompturilor;
- așezarea paginilor, după șabloanele din `web\templates\` și schițele din
  brainstorming;
- varianta de eval pentru consistență, din 9.

## 11 · Riscuri și lucruri neverificate

- **Creditele din AI Pro.** Google nu spune dacă abonamentul primit prin
  oferta pentru studenți intră la beneficiu și nici dacă România e inclusă.
  Primul pas din plan e activarea creditelor. Dacă nu merg, varianta de
  rezervă e OpenAI, plătit, prin același fișier de furnizor.
- **Cardul.** Contul de facturare Google Cloud cere probabil un card, chiar
  dacă plătesc creditele.
- **Prețul pe imagine** e luat de pe pagina de prețuri Google, citită pe 31
  octombrie 2026: 0,0336 dolari la 1K. Se verifică la prima rulare.
- **Clasamentul e preliminar.** Scorurile Arena pentru Nano Banana 2.1 erau
  marcate „preliminary” pe 26 octombrie 2026.
- **Siglele mărcilor reale.** Modelul poate refuza sau deforma sigla unei
  mărci cunoscute. Pentru demo se folosesc branduri inventate, cu sigle
  proprii.
- **SynthID.** Toate imaginile Gemini au un filigran invizibil. Nu afectează
  aplicația, dar e bine de știut în lucrare.

## 12 · Estimare

Estimare grosieră, cam 57 de ore brute:

| Ce | Ore, cam |
|---|---|
| Conturile, formularul, lista cererilor, paginile de client și admin | ~20 |
| Generarea: setul complet, piesele, modificările | ~18 |
| Schemele noi, conversația pe toată cererea, desfacerea pe piese | ~10 |
| Pozele de referință, la Discovery și la generare | ~2 |
| Actualizarea specificațiilor la modificări | ~2 |
| Evals | ~5 |

O parte din contul de admin se suprapune cu modulul 4, UI-ul unificat, deci net
rămân cam 49 de ore peste roadmap-ul din 16 octombrie 2026.
