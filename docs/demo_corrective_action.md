# Demo case – Corrective action mode

A **fictional** case for demonstrating the corrective action mode. The company, people and numbers are invented. Copy each input into the matching step.

Open the tool in this mode: `?lang=en&mode=capa` (Finnish: `?lang=fi&mode=capa`).

The case is built so that one candidate action (B, retraining) treats a symptom rather than the cause. A good run should show the AI flagging that, without saying which action to choose.

---

## English

**Step 1 – Nonconformity description**

> During an audit at a pharmaceutical customer, the customer's auditor found that 14 calibration certificates issued by our calibration laboratory between March and May listed reference standard RS-104 as the traceability reference. RS-104 had been taken out of service on 3 March and replaced with RS-117. The measurements themselves were made with RS-117, so the results are valid, but the traceability information on the certificates is wrong. Immediate actions: the 14 certificates have been identified from the laboratory system and the customer has been informed in writing.

**Step 1 – Your root-cause hypothesis**

> Verified: the certificate template takes the reference standard ID from a manually maintained list. The list was not updated when RS-104 was replaced. The equipment replacement procedure has no step that requires updating the list, and the template does not check the ID against the equipment register. Hypothesis: the root cause is a gap in the equipment replacement procedure, not an individual error. 5 × why: wrong ID on certificate → list not updated → no one was responsible for updating it → the procedure does not mention the list → the list was added later as a workaround and never brought into the procedure.

**Step 2 – Candidate actions**

```
Action A: Reissue the 14 certificates with the correct traceability information
Action B: Retrain laboratory technicians to check certificate details before issuing
Action C: Add a step with sign-off to the equipment replacement procedure for updating the reference list
Action D: Link the certificate template directly to the equipment register so that retired standards cannot be selected
```

**Step 3 – Criteria**

```
Removes the root cause
Cost
Time to implement
Risk of introducing new problems
Need to update documented information
Impact on other sites
```

**Step 3 – Decision**

> We implement A (already in progress), C and D. B is not taken forward as a separate action, because the technicians followed the process as it was written. Owner: laboratory manager. A by 20 October, C by 15 November, D by 31 January. C covers the period until D is in place.

---

## Suomeksi

**Vaihe 1 – Poikkeaman kuvaus**

> Lääketeollisuusasiakkaan auditoinnissa asiakkaan auditoija havaitsi, että kalibrointilaboratoriomme maalis–toukokuussa myöntämissä 14 kalibrointitodistuksessa jäljitettävyyden vertailunormaaliksi oli merkitty RS-104. RS-104 oli poistettu käytöstä 3.3. ja korvattu RS-117:llä. Mittaukset tehtiin RS-117:llä, joten tulokset ovat päteviä, mutta todistusten jäljitettävyystieto on väärä. Välittömät toimet: 14 todistusta on tunnistettu laboratoriojärjestelmästä ja asiakkaalle on ilmoitettu kirjallisesti.

**Vaihe 1 – Oma juurisyyhypoteesi**

> Varmistettu: todistuspohja hakee vertailunormaalin tunnuksen käsin ylläpidetystä listasta. Listaa ei päivitetty, kun RS-104 korvattiin. Laitteen vaihtomenettelyssä ei ole vaihetta, joka edellyttäisi listan päivittämistä, eikä todistuspohja tarkista tunnusta laiterekisteriä vasten. Hypoteesi: juurisyy on aukko laitteen vaihtomenettelyssä, ei yksittäisen henkilön virhe. 5 × miksi: väärä tunnus todistuksessa → listaa ei päivitetty → kenelläkään ei ollut vastuuta päivityksestä → menettely ei mainitse listaa → lista lisättiin myöhemmin kiertotienä eikä sitä koskaan viety menettelyyn.

**Vaihe 2 – Toimenpide-ehdotukset**

```
Toimenpide A: Myönnetään 14 todistusta uudelleen oikeilla jäljitettävyystiedoilla
Toimenpide B: Koulutetaan laboratorioteknikot tarkistamaan todistusten tiedot ennen myöntämistä
Toimenpide C: Lisätään laitteen vaihtomenettelyyn kuitattava vaihe vertailulistan päivittämisestä
Toimenpide D: Kytketään todistuspohja suoraan laiterekisteriin, jolloin käytöstä poistettua normaalia ei voi valita
```

**Vaihe 3 – Kriteerit**

```
Poistaako juurisyyn
Kustannus
Toteutusaika
Uusien riskien mahdollisuus
Tarve päivittää dokumentoitua tietoa
Vaikutus muihin toimipisteisiin
```

**Vaihe 3 – Päätös**

> Toteutamme toimenpiteet A (käynnissä), C ja D. B:tä ei viedä eteenpäin erillisenä toimenpiteenä, koska teknikot toimivat kirjatun menettelyn mukaisesti. Vastuuhenkilö: laboratoriopäällikkö. A 20.10. mennessä, C 15.11. mennessä, D 31.1. mennessä. C kattaa ajan, kunnes D on käytössä.
