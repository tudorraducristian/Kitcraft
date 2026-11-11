# Kitcraft: client, admin și inspector, design

**Data:** 2026-11-05
**Status:** aprobat de Tudor pe 2026-11-05
**Înlocuiește:** `2026-10-31-personalizare-client-admin-design.md`.
Documentul de față e complet, nu trebuie citit împreună cu cel vechi.
**Sursa:** propunerile profesoarei de licență din 31 octombrie și 5 noiembrie 2026,
aduse de Tudor, și brainstormingurile din aceleași zile.

În document, ce nu e marcat a fost hotărât de Tudor. Ce a ales Claude e marcat
*Alegerea lui Claude*.

---

## 1 · Pe înțeles

Aplicația e un atelier de croitorie. Clientul vine la tejghea, adică în contul
lui, sau trimite o scrisoare, adică un email. Atelierul îl întreabă ce nu e clar,
îi face o schiță, iar clientul o aprobă sau cere schimbări.

Meșterul, adică adminul, compară apoi fiecare haină cu schița aprobată și scrie
câte o fișă. Șeful de atelier, adică inspectorul, se uită peste fișe și semnează
piesă cu piesă. Dacă șapca nu e bună, ea se întoarce la meșter, iar tricoul rămâne
semnat. Clientul află că totul e în regulă abia când toate piesele sunt semnate.

**Cât de greu e de explicat:** conturile, rubrica de emailuri, trimiterea
emailurilor și aprobarea inspectorului sunt ușoare, pentru că sunt aceleași idei ca
în aplicațiile web obișnuite. Două părți sunt grele:

1. **Imaginea unei piese trebuie să arate ca piesa din imaginea setului.** Soluția
   e la 9.4.
2. **Un răspuns scris liber pe email trebuie citit corect.** „Arată bine, dar fă
   șapca neagră” nu e o aprobare. Un „aprobat” citit greșit pornește tot lanțul.
   Soluția e la 9.7.

## 2 · De ce

Profesoara de licență a aprobat cele patru module din 16 octombrie 2026 și a cerut
pe 31 octombrie:

- generarea unei imagini pe baza descrierii, pentru un echipament complet;
- o parte de admin și una de client: clientul completează cererea în aplicație, pe
  profilul lui, și primește un model generat, iar adminul preia cererile de acolo;
- ca direcție de dezvoltare și scalabilitate, extinderea la un echipament complet,
  nu doar la tricouri.

Pe 5 noiembrie, Tudor și profesoara au adăugat:

- un istoric al comenzilor și un loc de vizualizare a contractelor în contul de
  client;
- emailuri automate la cererile din email, cu același drum ca la client;
- un cont de inspector, ca verificare umană;
- un anunț către client după aprobare.

Ce o face valoroasă pentru licență: lanțul se închide. Descrierea clientului devine
un model aprobat, modelul aprobat devine referința cu care se compară produsul, iar
un om semnează rezultatul agenților înainte ca modelul să meargă mai departe.

## 3 · Obiective

1. **Trei tipuri de cont:** client, admin și inspector.
2. **Două căi de intrare,** cu același drum: formularul clientului și emailul.
3. Clientul face o **cerere**: alege piesele, le descrie și poate încărca sigla și
   poze de referință.
4. **Întrebările de clarificare** ajung la client: în cont sau, automat, pe email.
5. Se generează **imaginile setului complet, față și spate**, pe care clientul le
   **aprobă** sau cere să le **modifice**. Abia după aprobare se fac **imaginile pe piese,
   față și spate**.
6. **Adminul** vede toate cererile, din ambele surse, are o **rubrică cu toate
   emailurile fiecărui client** și face verificările pe fiecare piesă.
7. **Inspectorul** vede imaginile aprobate de client, imaginile pieselor, pozele încărcate și
   rapoartele, apoi **aprobă sau trimite înapoi fiecare piesă**.
8. Când toate piesele sunt aprobate, **clientul primește confirmarea** pe calea pe
   care a venit cererea.
9. Contul de client are **istoricul comenzilor** și **vizualizarea contractelor**.
10. **Catalogul are șase piese,** iar o piesă nouă se adaugă doar cu o schemă nouă,
    fără cod. Ăsta e argumentul de scalabilitate cerut de profesoară.
11. **Fluxul A și Image Match rămân funcționale.** Imaginea aprobată a fiecărei piese
    devine referința pentru Image Match.

## 4 · Non-obiective

Lucruri care nu se fac, ca să nu crească proiectul:

- **analiza contractelor, agentul de research, procedurile și UI-ul unificat:**
  fiecare are specul lui, mai târziu. Aici, contractul doar se încarcă și se vede;
- **legătura cu producția și tricoul real de la producători:** apar doar ca direcție
  de viitor, vezi 15;
- verificarea automată a emailurilor la câteva minute. Rămâne butonul, ca azi;
- schimbarea pieselor unei cereri după ce a pornit. Pentru alte piese se face o cerere nouă;
- un pas în care adminul vede imaginea înainte să plece la client;
- generarea sau editarea contractelor în aplicație;
- nume și numere personalizate pe fiecare purtător;
- mărimi, cantități, prețuri, ofertare, plăți;
- găzduire publică: aplicația rămâne locală, pe laptop;
- resetarea parolei pe email, autentificarea în doi pași, logarea cu Google;
- clientul nu vede rapoartele de verificare și nici motivul pentru care o piesă s-a
  întors la admin;
- *Alegerea lui Claude:* anularea unei cereri, un chat între client și admin și
  unirea unui client de pe email cu un cont făcut mai târziu pe aceeași adresă.

## 5 · Anti-obiective

Situații în care proiectul a eșuat, chiar dacă tehnic rulează:

- **Piesele nu seamănă cu setul.** Dacă tricoul din imaginea lui are altă nuanță sau
  sigla în alt loc decât în imaginea completă, Image Match verifică produsul față de
  o referință greșită și tot lanțul își pierde sensul.
- **Generarea inventează.** Sigla deformată, text greșit pe produs, elemente pe care
  clientul nu le-a cerut.
- **Un răspuns e citit greșit ca aprobare.** Un model pe care clientul nu l-a aprobat
  merge mai departe. Când răspunsul nu e clar, nu se aprobă nimic.
- **Aplicația completează din burtă.** Valori pe care clientul nu le-a spus ajung în
  specificații.
- **Un email pleacă de două ori sau la altcineva.** Destinatarul e mereu expeditorul
  cererii, niciodată o adresă găsită în text.
- **Se strică ce merge azi.** Fluxul A și Image Match se comportă la fel. Testele
  rămân verzi, cu excepțiile de la 9.13.
- **Factura vine neanunțată.** Consum peste creditele lunare fără ca Tudor să știe.
- **O piesă nouă cere cod.** Atunci argumentul de scalabilitate cade.

## 6 · Ce a hotărât Tudor

### 6.1 · Pe 31 octombrie 2026

- Întrebările de clarificare le primește clientul, înainte de generare. Motivul lui
  Tudor: așa se preia direct ce vrea clientul.
- O modificare cerută de client actualizează și specificațiile, nu doar imaginea.
  Altfel, agentul din Fluxul A, care verifică față de specificații, și Image Match,
  care verifică față de imagine, s-ar contrazice pe același produs.
- Cazul principal e merch-ul unui brand. Clientul alege din tricou, hanorac, geacă,
  șapcă, șosete și pantaloni.
- O imagine cu setul complet, pentru client, și câte o imagine pe piesă, pentru Image
  Match, pentru că poza produsului e de obicei cu o singură piesă. Din 5 noiembrie, fiecare
  are față și spate, vezi 6.2.
- Furnizorul de imagini: Google, Gemini API, `gemini-nano-banana-2.1`, plătit din cei
  10 dolari pe lună de credite Google Cloud din Google AI Pro, cam 300 de imagini la
  1K. OpenAI `gpt-image-2.5-sunburst` e primul în clasamentul Arena, cu 1521 de puncte
  față de 1432, dar costă separat. Tudor a ales varianta gratuită.
- Aplicația se va numi **Kitcraft**. Folderul și repo-ul rămân `ciptronic-validator`.

### 6.2 · Pe 5 noiembrie 2026

**Emailul:**

- Adminul apasă un buton ca să vadă emailurile, cum e acum.
- Adminul preia cererea și o bagă în Discovery. Dacă mai sunt întrebări, ele pleacă
  automat la client.
- Adminul are o rubrică în care vede toate emailurile cu acel client și un buton care
  extrage răspunsurile primite.
- Mai multe piese în același email formează un singur set. Un tricou și o șapcă
  înseamnă un singur email cu poza ambelor și un singur email cu întrebările pentru
  ambele.
- Și două tricouri diferite rămân în același email, ca clientul să nu răspundă la două
  conversații în paralel.
- Modificările cerute pe email merg ca în cont, cu aceeași limită de 5 runde.
- Imaginea generată pleacă direct la client, fără să o vadă adminul înainte.
- Aprobarea sau modificarea se citește tot cu butonul „Extrage răspunsurile”.

**Piesele și vederile:**

- Fiecare piesă are două vederi, față și spate, cu câte o imagine și câte o poză de verificare.
  Așa se poate cere un tricou cu sigla pe piept și print pe spate.
- Piesele rămân cele alese la început. Pentru alte piese, clientul face o cerere nouă.

**Verificarea și inspectorul:**

- După ce clientul aprobă imaginea, adminul trece la verificări.
- Adminul dă verificările mai departe cu un buton, când le-a terminat pe toate piesele.
- Inspectorul, un om cu cont propriu, doar vizualizează și aprobă. Vede imaginea finală
  aprobată de client, imaginile pieselor, poza încărcată de admin și rapoartele.
- Inspectorul decide pe fiecare piesă. Dacă doar șapca nu e în regulă, adminul reface
  doar șapca și o retrimite, iar piesele aprobate rămân aprobate.
- La trimiterea înapoi, inspectorul scrie ce nu e bine, iar adminul poate încărca altă
  poză.

**Clientul:**

- Doar când toate piesele sunt aprobate primește clientul confirmarea.
- Clientul cu cont primește mesajele direct în interfață. Emailul e doar pentru cererile
  venite pe email.
- La apăsarea aprobării, confirmarea pleacă singură. Nu o scrie inspectorul de mână.
- Cât timp o piesă se reface, clientul vede doar „în verificare”, fără motiv și fără
  rapoarte.

**Contractele:**

- Aplicația nu scrie contractul. Firma îl are deja, ca PDF.
- Adminul îl încarcă la cerere, după ce clientul aprobă modelul.
- Clientul cu cont îl vede în interfață, doar pentru citire. Clientul de pe email îl
  primește pe email.

## 7 · Cum arată

Schițele sunt schițe de discuție, nu design vizual final. Stau în AIS-OS, ignorate de
git:

- `.superpowers\brainstorm\1612-1793449020\content\`: `drum-cerere.html`,
  `client-model-v2.html`;
- `.superpowers\brainstorm\825-1793879636\content\`: `rubrica-emailuri.html`,
  `ecran-inspector-v2.html`.

Schițele arată o singură vedere pe piesă, pentru că hotărârea cu față și spate a venit după ele.

### 7.1 · Clientul cu cont

1. **Contul.** Își face singur cont, cu email, parolă și numele brandului.
   *Alegerea lui Claude.*
2. **Cerere nouă.** Alege piesele din catalog, cel puțin una și cel mult 6. Aceeași piesă
   poate apărea de mai multe ori: două tricouri diferite apar ca „Tricou 1” și „Tricou 2”, în
   aceeași cerere și în aceleași imagini de set, la fel ca pe email. Scrie descrierea. Încarcă
   opțional sigla și până la 6 poze de referință. *Regula pieselor și numărul de poze sunt
   alegerea lui Claude:* Nano Banana 2.1 primește până la 10
   imagini de obiect pe cerere, iar restul locurilor rămân pentru siglă și imaginea
   completă.
3. **Întrebările.** Discovery pune întrebări în maximum 5 runde **pentru toată
   cererea**, cu cel mult 8 întrebări pe rundă, grupate pe teme. Discovery vede și pozele
   de referință, ca să nu întrebe ce se vede deja în ele. *Alegerea lui Claude.*
   Dacă din descriere reiese o siglă, iar fișierul lipsește, Discovery îl cere, iar pagina
   de întrebări permite încărcarea lui și a altor poze. Un print descris în cuvinte, cum e
   un text sau niște dungi, se generează din descriere. Dacă clientul spune că nu are
   fișier, generarea lucrează din descriere, iar clientul judecă rezultatul. *Alegerea lui
   Claude.*
4. **Ce a rămas necompletat.** Dacă după ultima rundă mai sunt câmpuri goale, clientul
   primește un formular scurt doar cu ele, cu sugestii din indiciile schemei. Schemele nu
   au liste închise, deci sugestiile nu limitează răspunsul. Un răspuns ca „la alegerea
   voastră” e un răspuns al clientului și se păstrează ca atare. Generarea pornește abia
   când specificația fiecărei piese e completă. Până atunci, cererea așteaptă. *Alegerea
   lui Claude.*
5. **Modelul setului.** Aplicația generează două imagini ale setului complet, una cu fețele
   pieselor și una cu spatele lor. Clientul le aprobă împreună. *Cele două imagini sunt alegerea
   lui Claude:* o singură imagine cu 12 vederi ar ieși prea mică la 1K, iar clientul trebuie să
   vadă spatele înainte să-l aprobe.
6. **Aprob sau cer modificări.** La „cer modificări”, clientul scrie ce vrea schimbat.
   Întâi un pas cu Claude schimbă în specificații câmpurile atinse, apoi ambele imagini se
   refac, fiecare pornind de la cea precedentă. Unele modificări nu au câmp în specificații, cum
   e „dungile mai late”. Pe acelea le poartă doar imaginea, iar Image Match le verifică.
   Sunt permise **cel mult 5 runde de modificări pe cerere**, ca să rămână în credite.
   După ultima, mai rămâne doar aprobarea. *Limita e alegerea lui Claude.* Dacă o modificare
   lasă câmpuri goale, de exemplu „pune sigla pe piept” la o piesă fără branding, cererea se
   întoarce la întrebări doar pentru ele, în aceeași limită de 5 runde, apoi imaginile se
   refac. *Alegerea lui Claude.* Modificarea nu poate schimba piesele: la „adaugă o șapcă”,
   clientul e anunțat că pentru alte piese face o cerere nouă.
7. **Piesele, după aprobare.** Aplicația face imaginile pe piese o singură dată: fața fiecărei
   piese din imaginea aprobată cu fețele, spatele din imaginea aprobată cu spatele. Clientul le
   vede, dar nu le aprobă separat. *Alegerea lui Claude:* o rundă de modificări costă astfel
   două imagini, nu paisprezece.
8. **Cererile mele și istoricul.** O listă cu toate cererile lui și starea fiecăreia.
   Istoricul comenzilor sunt chiar cererile lui, cele validate și cele în curs, pentru
   că prețurile și cantitățile rămân în afara proiectului. *Alegerea lui Claude.*
9. **Mesajele.** Confirmarea apare în interfață, la cererea respectivă și ca semn pe
   lista de cereri. Nu e o căsuță de mesaje separată. *Alegerea lui Claude.*
10. **Contractele.** O pagină cu contractele lui, deschise doar pentru citire, și o
    trimitere din fiecare cerere care are contract. *Alegerea lui Claude.*

### 7.2 · Clientul de pe email

Clientul nu are cont. Drumul lui e același, dar totul se întâmplă pe email, într-o
singură conversație:

1. Trimite un email cu cererea, eventual cu poze sau PDF.
2. Dacă lipsesc detalii, primește un singur email cu toate întrebările, pentru toate
   piesele. Limitele sunt ca în cont: 5 runde, cel mult 8 întrebări pe rundă. *Limitele
   sunt alegerea lui Claude.*
3. Dacă după ultima rundă tot lipsesc câmpuri, ultimul email le cere pe cele rămase, cu
   sugestii din indiciile schemei. Asta ține locul formularului scurt din cont. Cererea
   așteaptă până vin. Dacă lipsește sigla, clientul o poate atașa la orice răspuns.
   *Alegerea lui Claude.*
4. Când cererea e completă, primește un singur email cu cele două imagini ale setului, față
   și spate.
5. Răspunde că aprobă sau scrie ce vrea schimbat. La o modificare primește un email nou,
   cu imaginile refăcute, de cel mult 5 ori. După ultima, un email cu text fix îi spune că mai
   poate doar să aprobe. Dacă cere alte piese, un email cu text fix îi spune că pentru ele
   trimite o cerere nouă. *Textele sunt alegerea lui Claude.*
6. Dacă răspunsul nu e clar, primește un email cu text fix, care îl roagă să spună dacă
   aprobă sau ce vrea schimbat. Nu se aprobă nimic. *Alegerea lui Claude.*
7. Dacă firma îi trimite un contract, îl primește ca PDF atașat.
8. Când toate piesele sunt aprobate, primește emailul de confirmare.

Imaginile pe piese nu i se trimit. Rămân pentru admin și inspector. *Alegerea lui
Claude.*

### 7.3 · Adminul

1. **Contul.** Unul singur, al lui Tudor, creat la instalare, nu prin înregistrare
   publică. *Alegerea lui Claude.*
2. **Lista cererilor.** Toate cererile, din ambele surse, cu sursa, clientul, piesele și
   starea. Piesele întoarse de inspector se văd separat, cu motivul. O cerere care așteaptă
   la nesfârșit rămâne în listă, vizibilă. Nu există o acțiune de închidere, iar pentru un
   demo local asta nu strică nimic. *Alegerea lui Claude.*
3. **Rubrica de emailuri,** ca în `rubrica-emailuri.html`:
   - sus, butonul „Verifică emailuri”, cu intervalul de date de azi;
   - în stânga, clienții, câte unul pe adresă de email, cu un semn când au un răspuns nou;
   - în dreapta, toate emailurile cu acel client, primite și trimise, în ordine;
   - la o cerere nouă, butonul „Preia cererea”;
   - la un răspuns primit, butonul „Extrage răspunsurile”.
4. **Preia cererea.** Cererea intră în Discovery. Dacă mai sunt întrebări, emailul pleacă
   singur. Dacă nu sunt, imaginea se generează și pleacă singură.
5. **Extrage răspunsurile.** Răspunsul se citește, iar aplicația arată ce a înțeles. Apoi
   face singură pasul următor, vezi 8.3. Fiecare apăsare citește un singur email și nu
   mai poate fi repetată pe același email. *Alegerea lui Claude.*
6. **Cererea deschisă.** Descrierea, sigla, pozele, întrebările și răspunsurile,
   specificațiile fiecărei piese, imaginile setului și imaginile pe piese, cu cele aprobate
   marcate. Specificațiile se pot descărca pe fiecare piesă. *Descărcarea e alegerea lui
   Claude.*
7. **Refacerea unei imagini de piesă.** Dacă o vedere a unei piese nu seamănă cu setul,
   adminul o poate reface de cel mult 2 ori. *Alegerea lui Claude.*
8. **Verificările, pe fiecare piesă.** Adminul încarcă două poze, față și spate, iar
   verificările pornesc pe ele. Agentul din Fluxul A le primește pe amândouă și le compară cu
   specificațiile piesei, pe trei zone, într-un singur raport. Image Match compară fiecare poză
   cu imaginea aprobată a aceleiași vederi, criteriu cu criteriu, în câte un raport. *Felul în
   care se leagă pozele de rapoarte e alegerea lui Claude.* Adminul poate încărca altă poză, iar
   verificarea piesei se reface. Inspectorul vede doar ultima variantă, iar rapoartele vechi rămân
   în baza de date. *Alegerea lui Claude.*
9. **De unde vine poza.** Aplicația nu ține evidența de unde vine, ca azi. *Alegerea lui
   Claude,* pornind de la hotărârea lui Tudor că pentru moment rămâne așa. Vezi 15.
10. **Trimite la inspector.** Butonul se activează când toate piesele neaprobate au toate cele
    trei rapoarte. După o întoarcere, trimite doar piesele refăcute.
11. **Contractul.** Adminul încarcă PDF-ul la cerere, după aprobarea modelului. Încărcarea
    nu oprește și nu condiționează verificările. O cerere are un singur contract, iar o
    încărcare nouă îl înlocuiește. *Alegerea lui Claude.* La cererile din email, PDF-ul
    pleacă singur la client.
12. **Paginile de azi,** `/sessions/new`, `/matches/new` și cele care urmează, rămân și se
    comportă la fel, dar aparțin adminului. *Alegerea lui Claude.*
13. **Numărătoarea imaginilor,** vezi 9.10.

### 7.4 · Inspectorul

Ca în `ecran-inspector-v2.html`. **Inspector** înseamnă aici omul. Agentul din Fluxul A apare
în aplicație și în lucrare ca „verificare pe specificații”. În cod, numele `inspector` rămâne
neatins. *Alegerea lui Claude.*

1. **Contul.** Unul singur, creat la instalare, ca al adminului. *Alegerea lui Claude.*
2. **De verificat.** Lista cererilor cu piese trimise de admin, cu „1 din 2 piese aprobate”.
3. **Cererea deschisă.** Sus, cele două imagini ale setului, aprobate de client. Apoi, pentru
   fiecare piesă, pe fiecare vedere: imaginea aprobată și poza încărcată de admin, plus cele trei
   rapoarte. Aprobarea e pe piesă, nu pe vedere. *Alegerea lui Claude.*
4. **Pe fiecare piesă:** „Aprobă piesa” sau „Trimite piesa înapoi la admin”. Trimiterea
   înapoi cere un text cu ce nu e bine.
5. **Verificate.** Cererile validate, doar de citit. *Alegerea lui Claude.*
6. Inspectorul nu poate schimba nimic altceva: nu încarcă poze, nu reface imagini, nu
   vede rubrica de emailuri și nici paginile de azi.

## 8 · Stările

### 8.1 · Starea cererii

Aceleași stări pentru ambele surse. Numele din cod sunt ale builderului.

| Stare | Ce înseamnă | Ce vede clientul cu cont |
|---|---|---|
| nouă | extrasă din email, nepreluată încă de admin | nu există cont |
| în descriere | Discovery are întrebări fără răspuns, inclusiv după o modificare care a lăsat câmpuri goale | în descriere |
| model de aprobat | imaginile setului așteaptă răspunsul clientului | model de aprobat |
| aprobată | modelul e aprobat, piesele se fac sau sunt gata | aprobat, piese gata |
| în verificare | la admin, la inspector sau cu o piesă la refăcut | în verificare |
| validată | toate piesele sunt aprobate, confirmarea a plecat | validat |

### 8.2 · Starea piesei

```
de verificat -> verificată -> la inspector -> aprobată (rămâne așa)
      ^                            |
      +------ trimisă înapoi <-----+
```

- „Verificată” înseamnă că are toate cele trei rapoarte, nu că rapoartele sunt bune. Adminul
  decide dacă o trimite mai departe.
- Nu există o limită pentru câte ori se poate întoarce o piesă. *Alegerea lui Claude:* se
  întâmplă doar la apăsarea unui om și nu consumă imagini decât dacă adminul reface imaginea.
- Când ultima piesă e aprobată, cererea devine validată, iar confirmarea pleacă singură.
- Confirmarea e pe cerere. Un email dă o singură cerere, deci și o singură confirmare.
  *Alegerea lui Claude.*

### 8.3 · Ce face „Extrage răspunsurile”

| Cererea e în | Clientul a scris | Aplicația face singură |
|---|---|---|
| în descriere | răspunsuri, tot mai lipsesc câmpuri | pleacă următorul email cu întrebări |
| în descriere | răspunsuri, cererea e completă | se generează imaginile setului, sau se refac după o modificare, și pleacă pe email |
| model de aprobat | aprobă | cererea e aprobată, se fac imaginile pe piese |
| model de aprobat | cere o modificare | se schimbă specificațiile, se refac imaginile, pleacă pe email |
| model de aprobat | cere o modificare care lasă câmpuri goale | pleacă emailul cu întrebări doar pentru ele, cererea revine în descriere |
| model de aprobat | cere o modificare peste limita de 5 | pleacă emailul cu limita, starea nu se schimbă |
| model de aprobat | cere alte piese | pleacă emailul care îi spune să trimită o cerere nouă, starea nu se schimbă |
| model de aprobat | nu e clar | pleacă emailul cu text fix, starea nu se schimbă |

## 9 · Cum se leagă de cod

Codul de azi: FastAPI, HTMX, Jinja2, SQLite, Claude Sonnet 4.6 prin `agents\llm_client.py`.
Regulile din `CLAUDE.md`-ul proiectului rămân, cu o excepție, la 9.11.

### 9.1 · Piesele

- Cinci scheme noi în `schemas\`, în același format ca `tricou.json`: hanorac, geacă, șapcă,
  șosete, pantaloni. Câmpurile lor le scrie builderul după modelul tricoului.
- Regula rămâne: **o piesă nouă înseamnă doar `schemas\<nume>.json`**. Asta include generarea
  de imagini. Promptul de generare se construiește generic din câmpurile schemei.
- Schemele pot primi **chei opționale noi**, inclusiv `tricou.json`. Cheile spun dacă un câmp
  se vede într-o poză, cum nu se văd materialul sau tehnica, și dacă vine din identitatea
  comună a setului, cum vin culorile și sigla. Codul care nu le cunoaște le ignoră. Numele
  cheilor sunt ale builderului. *Alegerea lui Claude.*
- **Toate piesele au două vederi,** inclusiv șosetele, ca regula să rămână una singură. *Alegerea
  lui Claude.*
- **Câte un loc de branding pe fiecare parte.** Obiectul `branding` de azi rămâne pentru față. Se
  adaugă un al doilea obiect, în același format, pentru spate. `schemas\loader.py` știe deja
  obiectele de un nivel, deci nu e nevoie de imbricare nouă. *Alegerea lui Claude.*
- **Fluxul A de azi nu vede câmpul nou.** Schema îl marchează ca fiind doar pentru cereri, iar
  `loader` îl filtrează implicit, ca sesiunile operatorului și testele lor să rămână la fel.
  Cererile, emailul și agentul, când verifică o piesă dintr-o cerere, văd schema completă.
  *Alegerea lui Claude.*

### 9.2 · Cererea cu mai multe piese

- Constrângerea: **la final, fiecare piesă are propria specificație completă, în formatul de
  azi**, adică o sesiune Discovery cu `product_type` egal cu piesa. Așa agentul din Fluxul A,
  raportul și paginile de azi merg fără schimbări.
- Cum se poartă conversația pentru toată cererea se lasă la builder: fie o schemă compusă,
  desfăcută la final pe piese, fie sesiuni pe piese cu întrebările adunate într-o singură rundă.
  Atenție: `schemas\loader.py` știe azi un singur nivel de imbricare, iar
  `prompts\discovery.md` cere cel mult 4 întrebări pe rundă, pe un singur produs. Acel prompt
  rămâne pentru Fluxul A. Cererea cu mai multe piese are promptul ei.
- O piesă se identifică în cerere printr-un id propriu, nu prin `product_type`, pentru că
  același tip poate apărea de mai multe ori. Clientul o vede ca „Tricou 1”, „Tricou 2”.
  *Alegerea lui Claude.*
- Pentru cereri, specificația trebuie să fie completă înainte de generare. Pentru sesiunile de
  azi ale operatorului, comportamentul rămâne: după 5 runde sesiunea se închide chiar dacă e
  incompletă.
- Identitatea comună a setului, adică brandul, culorile, sigla și stilul, stă la nivel de
  cerere, nu se repetă pe fiecare piesă. Dacă o piesă are altă valoare, de exemplu un tricou
  negru și unul alb, valoarea piesei are prioritate. *Alegerea lui Claude.*

### 9.3 · De la email la set

- `email_extractor.extract` întoarce azi câte un `ProductRequest` pe produs și rămâne așa,
  împreună cu promptul lui. Peste rezultat se adaugă un pas în cod, care le adună într-o singură
  cerere. *Alegerea lui Claude.*
- **Un email dă o singură cerere,** oricâte produse ar avea. Tricou A, șapcă și tricou B devin o
  cerere cu trei piese, „Tricou 1”, „Șapcă” și „Tricou 2”. *Tudor a hotărât să rămână în același
  email. Felul în care se face e alegerea lui Claude.*
- **Un fir Gmail are o singură cerere,** deci un răspuns are mereu o singură țintă. *Alegerea lui
  Claude.*
- **Peste 6 produse.** Primele 6 intră în cerere, iar adminul vede restul în rubrică și le poate
  cere separat. *Alegerea lui Claude.*
- **De verificat.** Promptul spune azi „fiecare tip de produs”, deci două tricouri diferite pot
  ieși ca unul singur. Se verifică la evalurile pe `email_extractor` din roadmap. Doar dacă se
  întâmplă, se schimbă fraza aceea.
- Câmpurile găsite în email, `prefilled_state`, se păstrează pe fiecare piesă, ca azi, ca
  Discovery să nu întrebe ce s-a spus deja.
- Imaginile din email și din PDF devin poze de referință, cel mult 6, în ordinea din email.
  Imaginile sunt ale cererii, nu ale unei piese, pentru că extragerea nu le împarte pe produse.
  *Alegerea lui Claude.*
- **Sigla.** Promptul extragerii nu se schimbă. La „Preia cererea”, dacă emailul are imagini, un
  pas separat cu Claude vision, cu promptul lui în `.md`, spune care e sigla, iar alegerea se
  salvează pe cerere. Dacă nu e clar, primul email cu întrebări îl întreabă pe client, cu imaginile
  numărate în ordinea lor, sau îi cere s-o atașeze. Răspunsul nu e un câmp din schemă, deci pasul de
  la 9.7 îl întoarce separat. *Alegerea lui Claude.*

### 9.4 · Generarea imaginilor

- Un modul nou, de exemplu `image_gen\`, cu o singură interfață publică de trei operații:
  1. **setul complet**: fața, din identitate, specificațiile pieselor, siglă și pozele de
     referință; spatele, din aceleași date, cu imaginea fețelor folosită ca referință;
  2. **piesa, pe o vedere**: din imaginea aprobată a setului pentru acea vedere, plus specificația
     piesei și sigla;
  3. **modificarea**: din imaginea precedentă a fiecărei vederi și instrucțiunea clientului.
     Înainte de ea, specificațiile se actualizează cu un pas de text, cu Claude prin
     `agents\llm_client.py`.
- **Imaginea fiecărei piese se face din imaginea completă a aceleiași vederi, folosită ca
  referință,** nu separat din text. Asta e soluția pentru consistență: modelul primește setul deja desenat și i se cere
  să izoleze piesa, cu aceleași culori și aceeași siglă în același loc. *Alegerea lui Claude.*
- Piesele se generează pe fundal uniform, alb sau transparent, ca referința pentru Image Match
  să fie curată. *Alegerea lui Claude.*
- Furnizorul stă **într-un singur fișier**. Schimbarea pe OpenAI înseamnă un fișier nou și o
  setare, nu modificări prin aplicație.
- Prompturile de generare stau în `.md`, în `prompts\`, după regula de azi.
- Cheia stă în `.env`, ca `GEMINI_API_KEY`, și nu se comite niciodată.
- Rezoluția implicită e 1K. Mai mare doar dacă evals arată că 1K nu ajunge pentru Image Match.
- Aceleași trei operații servesc ambele căi de intrare.

### 9.5 · Legătura cu verificările

- Imaginea aprobată a fiecărei vederi se salvează și se dă ca `sim` lui `analyze_sim`, exact ca
  un mockup încărcat azi la `/matches`. Motorul din `image_matcher\` nu se schimbă și rămâne standalone.
- Cele două poze intră împreună în agentul din Fluxul A, care primește azi 1–4 poze. Fiecare
  intră ca `real` într-o rulare separată de Image Match, față de imaginea aceleiași vederi. O piesă
  are astfel un raport de la agent și două de la Image Match. *Alegerea lui Claude.*
- Rapoartele se salvează în tabelele de azi, `validation_reports` și `match_sessions`, legate de
  piesa din cerere prin tabelele noi.
- Inspectorul vede rapoartele prin aceleași șabloane, `report.html` și `match_report.html`, fără
  acțiuni pe ele. Adaptarea e a builderului.

### 9.6 · Citirea emailurilor

Butonul „Verifică emailuri” și intervalul de date rămân. În spate se schimbă patru lucruri,
găsite citind codul pe 5 noiembrie:

- **`fetch_emails` caută doar după date,** deci va aduce și emailurile trimise de aplicație, de
  îndată ce există trimitere. Ele trebuie excluse de la extragere.
- **`email_agent_fetch` nu salvează nimic** și cheamă LLM-ul pe fiecare email la fiecare apăsare.
  Emailurile se salvează acum, după `gmail_id`, iar fiecare trece o singură dată prin extragere.
  *Alegerea lui Claude:* rubrica are nevoie de ele, iar repetarea costă bani.
- **`EmailMessage` nu are `threadId`, `Message-ID` și `References`,** de care depinde legarea
  răspunsului de cerere. Se adaugă.
- **Un email de pe un fir cunoscut nu mai trece prin extragere ca cerere nouă.** Devine răspuns,
  în rubrică. Emailurile fără produs, de la adrese necunoscute, nu apar nicăieri, ca azi.

Un răspuns se leagă de cerere după firul Gmail. Un email de pe alt fir, de la un client cunoscut,
nu se leagă singur de nimic, pentru că poate fi o comandă nouă. Apare în rubrica clientului, trece
prin extragere, iar adminul alege: „Preia cererea”, dacă s-a găsit un produs, sau „Extrage
răspunsurile”, pentru una dintre cererile lui deschise. *Alegerea lui Claude:* o legătură automată
greșită poate duce la o aprobare falsă.

Rubrica se construiește din emailurile salvate. Adresa clientului se ia din antetul `From`.

### 9.7 · Citirea răspunsurilor

Azi, răspunsurile vin dintr-un formular, câmp cu câmp. Pe email, ele vin ca text liber. E nevoie de
un pas nou, cu Claude și cu promptul în `.md`, care primește **doar textul nou din răspuns**, fără
emailurile citate dedesubt, împreună cu întrebările trimise. *Alegerea lui Claude.*

- **La întrebări,** întoarce JSON: piesa, câmpul, valoarea. Regula e cea din `discovery.md`: nu
  inventează. Ce nu e spus rămâne gol și se întreabă din nou.
- **La imagine,** întoarce una dintre `aprobă`, `modificare`, `alte piese` sau `neclar`, plus textul
  modificării.
  Orice amestec, cum e „arată bine, dar fă șapca neagră”, e `modificare`. La orice îndoială, e
  `neclar`.
- Rezultatul trece printr-o verificare nouă în cod: cheile trebuie să fie din schemă.
  `discovery.parse_response` nu face asta azi. Valorile nu se verifică, pentru că schemele au doar
  indicii. Un răspuns de tipul „la alegerea voastră” se păstrează ca atare.
- Imaginile atașate la răspuns se salvează ca poze de referință, în limita de 6. Așa poate da clientul
  sigla mai târziu. *Alegerea lui Claude.*
- Răspunsul citit se arată adminului, ca să vadă ce a înțeles aplicația.

### 9.8 · Trimiterea emailurilor

- Azi nu există trimitere, iar `SCOPES` are doar `gmail.readonly`. Se adaugă `gmail.send`, ceea ce
  cere o autorizare nouă a contului `comenzi.ciptronic@gmail.com`.
- Tokenul care nu mai merge dă azi eroare 500. Dacă Google respinge tokenul, pagina cere
  reautorizare în loc să dea eroare, pentru că acum depinde de el și trimiterea. *Alegerea lui Claude.*
- Toate emailurile unei cereri pleacă în același fir Gmail, ca răspuns.
- **Destinatarul** e mereu adresa din `From` a primului email din cerere. Nu se ia din text, din PDF
  sau din răspunsul LLM. *Alegerea lui Claude.*
- **Conținutul** e un text fix din `.md`, plus întrebările generate sau imaginea, ca atașament. Nu se
  copiază text din emailul clientului. Emailurile sunt text simplu. *Alegerea lui Claude.*
- **Fiecare email trimis se salvează,** apare în rubrică și se trimite o singură dată pentru o acțiune.
- **Dacă trimiterea eșuează,** cererea nu trece mai departe, adminul vede eroarea și are un buton de
  reîncercare. *Alegerea lui Claude.*

Textele, scrise de builder, în română:

| Când pleacă | Ce conține |
|---|---|
| întrebări | întrebările, grupate pe piese |
| imaginile setului | cele două imagini și ce poate răspunde clientul |
| răspuns neclar | rugămintea de a spune dacă aprobă sau ce vrea schimbat |
| limita de modificări | mai poate doar să aprobe |
| alte piese | pentru ele trimite o cerere nouă |
| contract | PDF-ul atașat |
| confirmare | validarea a fost realizată și modelul urmează să fie trimis spre producție |

### 9.9 · Conținutul din afară

Emailul, PDF-ul și pozele vin de la oricine. *Alegerea lui Claude:*

- sunt date, nu instrucțiuni. Răspunsurile LLM-ului pe ele sunt doar JSON pe o schemă fixă;
- nimic nu pleacă înainte ca adminul să apese „Preia cererea”, așa că un email oarecare nu primește
  răspuns automat și nu consumă imagini;
- PDF-urile din emailuri trec prin hardening-ul de azi din `pdf_extractor`;
- contractele încărcate de admin se doar stochează și se servesc. Nu se parsează aici. Se verifică
  tipul și limita de 5 MB. Se servesc ca descărcare sau în vizualizatorul browserului, doar celui care
  are dreptul.

### 9.10 · Bugetul de imagini

- Aplicația numără imaginile generate și le arată adminului pe luna curentă.
- **Plafon lunar în aplicație,** setabil, implicit 280 de imagini, cam 9,4 dolari la 1K. La plafon,
  generarea se oprește cu un mesaj clar în aplicație. Clientul de pe email nu primește nimic, iar
  adminul vede cererea oprită și o poate relua. *Alegerea lui Claude.*
- O cerere cu șase piese consumă cel mult 12 imagini de set, 12 de piese și 24 de refaceri, adică
  48. O cerere obișnuită, cu două piese și două modificări, consumă 6 imagini de set și 4 de piese,
  adică 10.
- În Google Cloud se pune o alertă de buget la 10 dolari. Alerta doar anunță, oprirea o face plafonul.
- **Nicio cheltuială peste credite fără acordul explicit al lui Tudor.** Dacă creditele din AI Pro nu se
  activează, înainte de orice trecere pe OpenAI se revine la Tudor cu costul estimat.

### 9.11 · Conturile, și regula care se schimbă

- Regula de azi, „single-user, fără auth, deliberat”, se înlocuiește cu: **trei roluri, client, admin și
  inspector, tot local**. Regula „nu expune serverul pe rețea fără protecție” rămâne.
- Parolele se stochează doar ca hash, cu o bibliotecă standard. Sesiunea stă într-un cookie.
- Fiecare rol ajunge doar la paginile lui. Un client vede doar cererile, imaginile și contractele lui.
  `/healthz` rămâne public.
- Parolele inițiale ale adminului și inspectorului vin din `.env`, care nu se comite. *Alegerea lui Claude.*
- Încărcările de imagini au aceleași limite ca azi: 5 MB și verificarea tipului.
- `CLAUDE.md`-ul proiectului se actualizează cu regula nouă.

### 9.12 · Baza de date

Doar tabele noi, pentru utilizatori, cereri, piesele cererii, încărcări, imagini generate, emailuri,
deciziile inspectorului și contracte. Tabelele de azi, `discovery_sessions`, `validation_reports` și
`match_sessions`, rămân neschimbate. `db\schema.sql` folosește `CREATE TABLE IF NOT EXISTS`, deci baza
existentă nu se atinge. Structura exactă e a builderului.

### 9.13 · Testele

- Testele unitare și e2e folosesc un generator de imagini fals și un Gmail fals, la fel cum azi
  `get_llm_client` e înlocuit în teste. Nu cheamă API-urile.
- Testele care cheamă Gemini sau Gmail real stau separat, ca `tests\integration` azi.
- Cele 168 de teste existente trec în continuare, cu **o excepție deliberată**: drumul emailului se schimbă,
  deci testele din `tests\e2e\test_email_agent_routes.py` care îl descriu se rescriu, în principal
  `test_create_session_from_request` și `test_create_session_has_prefilled_state`. Fixture-ul comun
  `client` din `tests\conftest.py` poate intra logat ca admin. *Alegerea lui Claude.*
- Teste noi verifică:
  - fiecare rol ajunge doar la paginile lui, iar un client nu vede cererile altui client;
  - un email nu pleacă de două ori la apăsări repetate;
  - emailurile trimise de aplicație nu sunt citite ca cereri noi;
  - o piesă aprobată rămâne aprobată când altă piesă se întoarce;
  - confirmarea pleacă doar după ultima piesă aprobată, o singură dată, pe calea cererii;
  - un răspuns `neclar` nu aprobă nimic.

## 10 · Evals

Regula din roadmap: un modul e gata abia când are evals. Sunt cinci. *Pragurile, mărimea seturilor și regula
pentru rezultate slabe sunt alegerea lui Claude* și se revăd după prima rulare.

1. **Fidelitatea față de specificații.** Imaginile fiecărei piese, față și spate, trec împreună prin agentul din
   Fluxul A, ca și cum ar fi pozele produsului. O piesă trece dacă nu are niciun câmp neconform și dacă fiecare câmp care se vede într-o
   poză iese conform. Prag: cel puțin 80% din piese, la fiecare dintre 3 rulări.
2. **Consistența piesă–set.** Fiecare vedere a piesei se compară cu imaginea setului pentru aceeași vedere: culori,
   poziția siglei, elemente.
   Builderul alege între Image Match, cu piesa ca referință și setul ca „produs”, și un judecător cu Claude vision.
   Prag: cel puțin 80% din piese, la fiecare dintre 3 rulări.
3. **Sigla.** Sigla încărcată apare pe piesele pe care trebuie, nedeformată și neinversată. `image_matcher` are deja
   verificarea siglelor în oglindă. Prag: cel puțin 80% din piesele cu siglă, la fiecare dintre 3 rulări.
4. **Citirea răspunsurilor la întrebări.** Fiecare valoare extrasă apare chiar în răspunsul clientului. Prag: nicio
   valoare inventată, la fiecare dintre 3 rulări.
5. **Citirea răspunsurilor la imagine.** Un set de răspunsuri, inclusiv amestecate și ambigue, cu eticheta știută
   dinainte. Prag: **nicio aprobare falsă**, la fiecare dintre 3 rulări. O aprobare ratată costă doar un email în plus,
   pe când o aprobare falsă duce mai departe un model neaprobat.

**Mărimea seturilor.** Evalurile 1–3 folosesc 6 cereri cu câte două piese, iar fiecare rulare generează din nou
imaginile, ca să se măsoare și variația generatorului. O cerere are 2 imagini de set și 4 de piese, deci 6 × 3 × 6 =
108 imagini. Încap într-o lună, cu loc pentru o a doua trecere după o schimbare de prompt, dar nu pentru mai multe. Evalurile 4–5 au câte 20 de cazuri și nu consumă imagini.

**Dacă un eval nu trece pragul,** lucrul nu se oprește automat. Rezultatul ajunge la Tudor, iar faza următoare poate
porni, dar modulul nu e „gata” până nu trec toate. Dacă piesele tot nu seamănă cu setul după schimbările de prompt,
variantele se discută atunci cu Tudor.

## 11 · Ordinea de lucru

*Alegerea lui Claude.* Fiecare fază are planul ei, iar planurile se scriu toate înainte de execuție.

| Fază | Ce | Se poate arăta la final |
|---|---|---|
| 0 | activarea creditelor Google Cloud, pasul lui Tudor | o imagine generată cu cheia lui |
| 1 | cele trei conturi și protejarea paginilor de azi | fiecare rol ajunge doar la paginile lui |
| 2 | cererea din cont: piesele noi, conversația, generarea, modificările | clientul ajunge la model aprobat și piese |
| 3 | verificările pe piesă, inspectorul, confirmarea în interfață | lanțul complet, din cont |
| 4 | emailul: rubrica, trimiterea, setul, citirea răspunsurilor | lanțul complet, din email |
| 5 | istoricul și contractele | contul de client complet |

Evalurile se rulează la faza care le face posibile: 1–3 după faza 2, 4–5 în faza 4.

## 12 · Ce rămâne la builder

- mecanismul conversației pentru toată cererea, din 9.2;
- câmpurile celor cinci scheme noi;
- structura tabelelor și numele stărilor;
- biblioteca de hash și de sesiune;
- textul prompturilor și al emailurilor;
- cum se taie emailul citat dintr-un răspuns;
- cum arată așteptarea la operațiile lungi: aplicația are deja o pagină de așteptare la Image Match;
- așezarea paginilor, după șabloanele din `web\templates\` și schițele de la 7;
- varianta de eval pentru consistență, din 10;
- schimbarea numelui în Kitcraft în aplicație: titlul din `web\app.py`, șabloanele și `prompts\discovery.md`.

## 13 · Riscuri și lucruri neverificate

- **Creditele din AI Pro.** Google nu spune dacă abonamentul primit prin oferta pentru studenți intră la beneficiu și
  nici dacă România e inclusă. E faza 0. Dacă nu merg, varianta de rezervă e OpenAI, plătit, prin același fișier de
  furnizor, doar cu acordul lui Tudor.
- **Cardul.** Contul de facturare Google Cloud cere probabil un card, chiar dacă plătesc creditele.
- **Prețul pe imagine** e luat de pe pagina de prețuri Google, citită pe 31 octombrie 2026: 0,0336 dolari la 1K. Se
  verifică la prima rulare.
- **Clasamentul e preliminar.** Scorurile Arena pentru Nano Banana 2.1 erau marcate „preliminary” pe 26 octombrie 2026.
- **Siglele mărcilor reale.** Modelul poate refuza sau deforma sigla unei mărci cunoscute. Pentru demo se folosesc
  branduri inventate, cu sigle proprii.
- **SynthID.** Toate imaginile Gemini au un filigran invizibil. Nu afectează aplicația, dar e bine de știut în lucrare.
- **Spatele setului.** Imaginea cu spatele pornește de la cea cu fețele, iar modelul poate inventa detalii. De aceea
  o aprobă clientul și intră la evals. Că metoda dă rezultate bune e o presupunere, verificată la primele rulări.
- **Tokenul Gmail poate expira.** Dacă aplicația OAuth din Google Cloud e în „Testing”, tokenurile țin doar 7 zile, ceea ce
  nu e verificat. La susținere, emailul depinde de el. Se verifică la faza 4 și se mută, la nevoie, în „In production”.
- **Trimiterea din Gmail** poate fi marcată ca spam sau limitată. Pentru demo se folosesc adrese proprii.
- **Titlul lucrării** promite „validarea produsului finit”, iar în varianta de acum aplicația nu știe de unde vine poza
  verificată. Trebuie spus deschis în lucrare și pus lângă direcția de la 15.
- **Timpul,** vezi 14.

## 14 · Estimare

Estimare grosieră a lui Claude, pe aceeași scară cu cele 57 de ore din 31 octombrie:

| Fază | Ore, cam |
|---|---|
| 1 · Cele trei conturi | ~6 |
| 2 · Cererea din cont: formular, liste, piese, conversație, poze, generare, modificări, față și spate | ~51 |
| 3 · Verificările pe piesă, cu două vederi, inspectorul, confirmarea | ~12 |
| 4 · Emailul: rubrică ~6, trimitere ~5, set ~3, citirea răspunsurilor ~6, testele rescrise ~2 | ~22 |
| 5 · Istoricul și contractele | ~4 |
| Evals: cele trei vechi ~5, cele două noi ~3 | ~8 |
| **Total** | **~103** |

Sunt cam **46 de ore peste cele 57**, dintre care vreo 8 vin din față și spate.

**Ce înseamnă pentru roadmap:**

- totalul licenței crește de la cam 198 la cam 244 de ore;
- din 15 februarie până pe 26 aprilie, adică în cam 10 săptămâni, de lucrat ar fi cam 177 de ore, vreo 18 pe săptămână;
- la 8 ore pe săptămână lipsesc vreo 97, iar la 5–6 ore vreo 122;
- **la 8 ore pe săptămână, doar personalizarea nu încape în semestrul 2:** după cele 17 ore din ianuarie rămân vreo 86,
  adică aproape 11 săptămâni din cele 10. Contractele, research-ul, procedurile și UI-ul n-ar mai încăpea deloc până pe 1 mai.

Hotărârea rămâne a lui Tudor și se ia în februarie, cum era stabilit: mai multe ore, module tăiate sau micșorate, ori lucru în
pauze. Roadmap-ul și termenele din calendar se refac separat.

## 15 · Direcții de viitor

Spuse de Tudor pe 5 noiembrie 2026. Nu intră acum. În lucrare apar ca direcții de dezvoltare.

- **Tricoul real de la producători.** Producătorii fac un tricou real și îl trimit înapoi adminului. Poza lui devine poza de
  verificare pentru Image Match. Abia apoi vin verificarea și inspectorul, ca în acest design.
- **Mesajul către producție.** Când toate piesele sunt aprobate, inspectorul trimite și către producție, ca să știe că poate
  începe tricourile reale.

Ca să fie ușor de adăugat, tot ce se întâmplă la validarea unei cereri stă într-un singur loc în cod. *Alegerea lui Claude.*
