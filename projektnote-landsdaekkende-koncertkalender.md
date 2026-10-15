# Projektnote – Landsdækkende koncertkalender

**Version:** 1.0  
**Dato:** 14. oktober 2026  
**Formål:** Udvidelse af eksisterende HTML-koncertkalender på GitHub til en automatisk opdateret, landsdækkende koncertoversigt.

## 1. Projektets formål

Projektet skal samle koncerter fra danske spillesteder i én overskuelig koncertkalender.

Den eksisterende løsning omfatter allerede Train, VoxHall, Musikhuset Aarhus og Friheden. Den er baseret på HTML, GitHub og automatisk dataindsamling, herunder Playwright.

**Den eksisterende løsning skal videreudvikles – ikke erstattes.**

Målet er at skabe én samlet koncertoversigt, hvor brugeren kan finde koncerter, undersøge billetstatus og få information om eventuelle særlige adgangsforhold.

## 2. Geografisk afgrænsning

Projektet omfatter hele Danmark med følgende kriterier:

- Byer med mindst **20.000 indbyggere**.
- Indbyggertallet opgøres efter byområde, ikke kommunens samlede indbyggertal.
- Byer identificeres ud fra den senest tilgængelige officielle opgørelse fra Danmarks Statistik.
- Spillesteder i mindre byer medtages som udgangspunkt ikke.
- Hovedstadsområdet håndteres som et samlet byområde i den geografiske udvælgelse.

## 3. Krav til spillesteder

Et spillested kan optages, når alle følgende betingelser er opfyldt:

1. Spillestedet ligger i et kvalificeret byområde.
2. Det har en publikumskapacitet på mindst **150 personer** ved mindst én relevant koncertopstilling.
3. Det afholder offentligt tilgængelige koncerter.
4. Det har en hjemmeside med en offentlig koncert- eller eventkalender.
5. Koncertdata kan hentes teknisk, eksempelvis gennem Playwright, direkte HTML-aflæsning, strukturerede data eller API.

Spillesteder kan omfatte koncertsale, musikhuse, kulturhuse, spillesteder, klubber og multifunktionelle venues.

Kapacitet, kalenderadresse og adgang til koncertdata skal verificeres.

## 4. Data, der skal indsamles

For hver koncert skal systemet så vidt muligt indsamle:

- Kunstner eller koncertnavn.
- Dato og starttidspunkt.
- Spillested og by.
- Eventuel genre.
- Koncertbeskrivelse, hvis tilgængelig.
- Direkte link til koncerten.
- Billetlink.
- Billetpris, hvis tilgængelig.
- Billetstatus.
- Information om ledsagere og handicapadgang.
- Kilde og tidspunkt for seneste opdatering.

Manglende oplysninger må ikke opfindes.

## 5. Billetstatus

Systemet skal videreføre funktionaliteten fra den eksisterende koncertkalender.

Følgende statusser skal understøttes:

| Status | Betydning |
|---|---|
| Billetter tilgængelige | Salget er åbent, og tilgængelighed er bekræftet |
| Få billetter tilbage | Spillestedet eller billetudbyderen oplyser begrænset antal |
| Udsolgt | Koncerten er markeret som udsolgt |
| Venteliste | Der findes en venteliste |
| Ikke til salg endnu | Billetsalget er endnu ikke åbnet |
| Aflyst | Koncerten er aflyst |
| Flyttet | Dato eller spillested er ændret |
| Ukendt | Ingen pålidelig statusinformation er tilgængelig |

Statusser skal kun vises, når de er dokumenteret af kilden. Systemet må eksempelvis ikke konkludere, at en koncert er udsolgt, blot fordi billetknappen mangler.

Venteliste og udsolgt skal kunne eksistere samtidig, da en udsolgt koncert godt kan tilbyde venteliste.

## 6. Ledsagerordninger og tilgængelighed

Dette er et særligt vigtigt område i projektet.

For hvert spillested skal vi undersøge:

- Om der tilbydes gratis adgang for handicappedes ledsagere.
- Om der kræves gyldigt ledsagerkort.
- Om ledsagerbillet skal bestilles på forhånd.
- Om ledsagerbillet kan bestilles online.
- Om spillestedet skal kontaktes via telefon eller e-mail.
- Om der findes særlige kørestolspladser.
- Om der gælder særlige regler ved udsolgte koncerter.
- Om der er begrænsninger eller særlige procedurer.

Oplysningerne skal opdeles i:

**Spillestedsregler:** Generelle adgangs- og ledsagerregler, som gælder for spillestedet.

**Koncertspecifikke regler:** Særlige betingelser, der gælder for den enkelte koncert.

Hver oplysning skal ledsages af en kilde og dato for seneste verifikation.

Hvis der ikke findes oplysninger, skal systemet angive *Ikke oplyst* og ikke antage, at ledsageradgang er gratis eller mulig.

## 7. Teknisk arkitektur

Den eksisterende GitHub-løsning skal undersøges og genbruges.

Dataindsamling prioriteres i denne rækkefølge:

1. Officielle API'er eller strukturerede eventdata.
2. Direkte aflæsning af HTML.
3. Playwright til dynamiske hjemmesider.
4. Specialtilpassede integrationer, hvor de øvrige metoder ikke er tilstrækkelige.

Der oprettes et centralt spillestedsregister med oplysninger om navn, by, kapacitet, hjemmeside, kalenderadresse, indsamlingsmetode og teknisk status.

Alle koncerter normaliseres til én fælles datastruktur, som den eksisterende HTML-kalender kan anvende.

## 8. Automatisk opdatering

Automatisk opdatering er et ufravigeligt krav.

- Systemet skal opdatere koncertkalenderen uden manuel indgriben.
- Den eksisterende opdateringsmekanisme genbruges, hvis den er egnet.
- Nye koncerter skal automatisk tilføjes.
- Ændringer i dato, spillested og billetstatus skal registreres.
- Aflysninger og flytninger skal håndteres.
- Dubletter skal identificeres og samles.
- Fejl i én kilde må ikke forhindre opdatering fra øvrige spillesteder.
- Seneste vellykkede opdatering registreres for hvert spillested.
- Ved fejl må tidligere indsamlede oplysninger ikke fejlagtigt fremstå som aktuelle.
- Hentning skal respektere hjemmesidernes adgangsbetingelser og begrænsninger.

Billetstatus kan ændre sig hurtigt. Derfor skal systemet vise, hvornår oplysningerne sidst blev kontrolleret, og ikke garantere realtidsstatus.

## 9. Brugeroplevelse

Den eksisterende kalender skal som minimum bevare sine nuværende funktioner.

Den landsdækkende udgave skal kunne understøtte:

- Søgning efter kunstner eller koncert.
- Filtrering efter by og spillested.
- Filtrering efter dato eller periode.
- Visning af billetstatus.
- Direkte adgang til billetkøb og ventelister.
- Adgang til information om ledsagerordninger.
- Mobilvenlig visning.

Yderligere funktioner skal vurderes efter gennemgang af den eksisterende løsning, så der ikke udvikles noget, som allerede fungerer.

## 10. Implementeringsplan

**Fase 1 – Analyse af eksisterende løsning**

Gennemgå GitHub-repository, Playwright-scripts, datastruktur, automatiske opdateringer og brugergrænseflade.

**Fase 2 – National kortlægning**

Identificer samtlige danske byområder med mindst 20.000 indbyggere. Kortlæg relevante spillesteder og verificer kapacitet, hjemmeside og koncertkalender.

**Fase 3 – Teknisk klassifikation**

Undersøg hvert spillesteds kalender og identificer den bedst egnede indsamlingsmetode.

**Fase 4 – Integration**

Udvid dataindsamlingen og tilslut nye spillesteder. Genbrug fælles integrationer, hvor det er muligt.

**Fase 5 – Billetstatus og ledsagerinformation**

Implementer fælles håndtering af billetstatus og særskilt registrering af generelle og koncertspecifikke ledsagerregler.

**Fase 6 – Automatisering og kvalitetssikring**

Test dataindsamling, opdateringer, fejlhåndtering, dubletkontrol og visning på tværs af spillesteder.

## 11. Forventede leverancer

Projektet skal resultere i:

1. Et nationalt spillestedsregister med verificerede kildeoplysninger.
2. En maskinlæsbar datafil, eksempelvis `venues.json`.
3. En fælles datastruktur for koncerter og billetstatus.
4. Et register over ledsagerordninger og særlige adgangsforhold.
5. Udvidede Playwright-/dataindsamlingsintegrationer.
6. Automatisk opdatering via den eksisterende GitHub-løsning.
7. En opdateret landsdækkende HTML-koncertkalender.
8. Dokumentation for vedligeholdelse og tilføjelse af spillesteder.

## 12. Grundlæggende projektprincip

**Vi bygger videre på det, der allerede fungerer.**

Projektet skal ikke udvikles som en ny selvstændig koncertplatform, før den eksisterende løsning er gennemgået.

Første opgave er at etablere et korrekt og verificeret datagrundlag. Derefter udvides dataindsamlingen systematisk.

Målet er en landsdækkende koncertkalender, der er automatisk opdateret, overskuelig og særlig nyttig for personer, der har behov for information om ledsageradgang og tilgængelighed.
