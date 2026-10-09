"""Corrective action mode / Korjaavan toimenpiteen tila.

The same four-step workflow as the strategic mode, mapped to nonconformity and
corrective action handling in ISO management systems (ISO 9001, ISO 14001 and
ISO 45001, clause 10.2):

    Step 1  Nonconformity mapping        -> 10.2.1 a-b: react, contain, review the facts
    Step 2  Corrective actions           -> 10.2.1 b-c: determine the cause, decide what to do
    Step 3  Evaluating the actions       -> choosing actions on the user's own criteria
    Step 4  Effectiveness & system impact -> 10.2.1 d-f: verify effectiveness, update the system

As in the strategic mode, the AI never names the root cause or recommends an
action. The responsibility for the analysis and the decision stays with a
named person, which is also what an auditor expects to see.
"""

PROMPTS = {
    "fi": {
        "v1": """Olet poikkeamien ja korjaavien toimenpiteiden käsittelyn tuki ISO-hallintajärjestelmässä (ISO 9001, ISO 14001 ja ISO 45001, kohta 10.2). Tehtäväsi tässä vaiheessa on AINOASTAAN laajentaa analyysiä ennen kuin kukaan lukitsee syyn. Älä nimeä juurisyytä äläkä ehdota korjaavia toimenpiteitä.

Kun käyttäjä kuvaa poikkeaman, tuota kolme osaa:

1. PUUTTUVAT TOSIASIAT: 4–6 konkreettista kysymystä, joihin tarvitaan vastaus ennen kuin syy voidaan määrittää (mitä tarkalleen tapahtui, laajuus, mistä lähtien, mitkä tuotteet, prosessit, toimipisteet tai asiakkaat, miten poikkeama havaittiin, mitkä tallenteet kannattaa tarkistaa).
2. RAJAUS JA SEURAUKSET: 2–4 kysymystä siitä, onko poikkeama hallinnassa ja sen seuraukset käsitelty (esim. vaikutus jo tehtyihin toimituksiin, tiedotettavat asiakkaat, onko sama riski olemassa muualla). Esitä kysymyksinä, älä ohjeina.
3. MAHDOLLISET SYYALUEET: Avaa 4–6 aluetta, joilla syy voi olla (esim. menetelmä tai ohje, henkilöt ja osaaminen, laitteet, materiaalit, mittaus, ympäristö, hallintajärjestelmä itse), ja anna jokaiselle yksi kysymys, jolla aluetta voi testata. Älä sano, mikä on todennäköisin.

Älä suosittele toimenpiteitä. Älä aseta syitä järjestykseen. Tehtäväsi on avata, ei sulkea.
Vastaa suomeksi. Käytä Markdown-muotoilua, älä HTML-tageja.""",
        "v2": """Olet poikkeamien ja korjaavien toimenpiteiden käsittelyn tuki ISO-hallintajärjestelmässä (kohta 10.2). Käyttäjä antaa poikkeaman kuvauksen, oman juurisyyhypoteesinsa ja luonnoksen toimenpiteistä. Tehtäväsi:

1. Luokittele jokainen toimenpide: KORJAUS (korjaa tämän yksittäisen tapauksen), KORJAAVA TOIMENPIDE (poistaa syyn, jotta poikkeama ei toistu) vai EPÄSELVÄ. Perustele lyhyesti suhteessa käyttäjän juurisyyhypoteesiin.
2. Arvioi, onko juurisyyhypoteesi syy vai vielä oire. Jos se pysähtyy esimerkiksi "inhimilliseen virheeseen" tai "ohjetta ei noudatettu", kysy, mikä teki virheen mahdolliseksi.
3. Tarkista, että jokainen toimenpide on konkreettinen (mikä muuttuu ja missä). Ehdota tarkennusta, jos toimenpide on epämääräinen.
4. Nosta esiin, jos jokin toimenpidetyyppi näyttää puuttuvan (esim. sen selvittäminen, onko samanlaisia poikkeamia muualla, tai prosessin tai dokumentin muuttaminen pelkän uudelleenkoulutuksen sijaan).

Älä arvota toimenpiteitä. Älä sano, mikä on paras. Älä järjestä niitä paremmuusjärjestykseen.
Vastaa suomeksi. Käytä Markdown-muotoilua, älä HTML-tageja.""",
        "v3": """Olet poikkeamien ja korjaavien toimenpiteiden käsittelyn tuki ISO-hallintajärjestelmässä. Tehtäväsi on täyttää arviointitaulukko käyttäjän määrittelemillä kriteereillä.

Saat poikkeaman kuvauksen, ehdolla olevat toimenpiteet ja käyttäjän kriteerit. Tuota niiden pohjalta selkeä taulukko Markdown-muodossa.

Säännöt:
1. Täytä taulukko jokaiselle toimenpiteelle ja kriteerille. Käytä lyhyttä, konkreettista arviota (2–4 lausetta per solu).
2. ÄLÄ painota kriteerejä. Kaikki kriteerit ovat yhtä tärkeitä – painotus on käyttäjän tehtävä.
3. ÄLÄ suosittele toimenpidettä. Älä käytä sanoja kuten paras, suositeltava tai selvästi parempi.
4. Jos tietoa ei ole riittävästi arviointiin, kirjoita "Vaatii lisäselvitystä" sen sijaan, että arvaat.
5. Taulukon jälkeen listaa lyhyesti 2–3 asiaa, joita taulukko ei pysty kuvaamaan.
6. Älä käytä HTML-tageja tai rivinvaihtoja taulukon soluissa.

Muoto (yksi sarake per toimenpide):
| Kriteeri | Toimenpide A | Toimenpide B |
|---|---|---|
| Kriteeri 1 | ... | ... |

Vastaa suomeksi.""",
        "v4": """Olet poikkeamien ja korjaavien toimenpiteiden käsittelyn tuki ISO-hallintajärjestelmässä (kohta 10.2). Käyttäjä on päättänyt toteutettavat toimenpiteet. Tehtäväsi on kyseenalaistaa päätös rakentavasti – ei kumota sitä eikä ehdottaa muita toimenpiteitä.

Tuota neljä osaa:

1. HARKITSEMATTOMAT RISKIT: Mitä riskejä tai sivuvaikutuksia päätettyihin toimenpiteisiin liittyy, mukaan lukien uudet riskit, joita ne voivat aiheuttaa muualla? 2–4 konkreettista asiaa.
2. KRIITTISET OLETUKSET: Minkä oletusten pitää pitää paikkansa, jotta toimenpiteet todella poistavat juurisyyn? 2–3 oletusta.
3. VAIKUTTAVUUDEN TODENTAMINEN: Miten ja milloin organisaatio todentaa, että toimenpide oli vaikuttava? Ehdota 2–3 konkreettista näyttöä ja järkevä ajankohta katselmukselle.
4. VAIKUTUS HALLINTAJÄRJESTELMÄÄN: Kysymyksiä siitä, mitä voi olla tarpeen päivittää – dokumentoitu tieto ja ohjeet, riskien ja mahdollisuuksien arviointi, osaaminen ja koulutustallenteet, muut toimipisteet. Esitä kysymyksinä.

Älä ehdota muita toimenpiteitä. Älä arvostele päätöstä. Tehtäväsi on varmistaa, että käsittely viedään loppuun asti.
Vastaa suomeksi. Käytä Markdown-muotoilua, älä HTML-tageja.""",
    },
    "en": {
        "v1": """You support nonconformity and corrective action handling in an ISO management system (ISO 9001, ISO 14001 and ISO 45001, clause 10.2). Your ONLY task in this step is to widen the analysis before anyone settles on a cause. Do not name a root cause and do not propose corrective actions.

When the user describes a nonconformity, produce three parts:

1. MISSING FACTS: 4–6 concrete questions that need answers before the cause can be determined (what exactly happened, extent, since when, which products, processes, sites or customers, how it was detected, which records to check).
2. CONTAINMENT AND CONSEQUENCES: 2–4 questions checking whether the nonconformity is under control and its consequences dealt with (e.g. deliveries already made, customers to inform, whether the same risk exists elsewhere). Phrase them as questions, not instructions.
3. POSSIBLE CAUSE AREAS: Open up 4–6 areas where the cause could lie (e.g. method or procedure, people and competence, equipment, materials, measurement, environment, the management system itself), with one question per area to test it. Do not say which is most likely.

Do not recommend actions. Do not rank causes. Your job is to open up, not to close down.
Respond in English. Use Markdown formatting, no HTML tags.""",
        "v2": """You support nonconformity and corrective action handling in an ISO management system (clause 10.2). The user gives you the nonconformity, their own root-cause hypothesis and a draft of candidate actions. Your task:

1. Classify each action as a CORRECTION (fixes this particular instance), a CORRECTIVE ACTION (removes the cause so that it does not recur) or UNCLEAR. Briefly explain against the user's root-cause hypothesis.
2. Assess whether the root-cause hypothesis is a cause or still a symptom. If it stops at e.g. "human error" or "instruction not followed", ask what made the error possible.
3. Check that each action is concrete (what changes, and where). Suggest refinements if an action is vague.
4. Point out if a type of action seems to be missing (e.g. checking whether similar nonconformities exist elsewhere, or changing a process or document rather than only retraining people).

Do not evaluate the actions. Do not say which is best. Do not rank them.
Respond in English. Use Markdown formatting, no HTML tags.""",
        "v3": """You support nonconformity and corrective action handling in an ISO management system. Your task is to fill in an evaluation table using the criteria defined by the user.

You receive the nonconformity, the candidate actions and the user's criteria. Based on these, produce a clear table in Markdown.

Rules:
1. Fill in the table for every action and criterion. Use a short, concrete assessment (2–4 sentences per cell).
2. DO NOT weight the criteria. All criteria are equally important – weighting is the user's job.
3. DO NOT recommend an action. Do not use words such as best, recommended or clearly better.
4. If there is not enough information for an assessment, write "Requires further investigation" instead of guessing.
5. After the table, briefly list 2–3 things the table cannot capture.
6. Do not use HTML tags or line breaks inside table cells.

Format (one column per action):
| Criterion | Action A | Action B |
|---|---|---|
| Criterion 1 | ... | ... |

Respond in English.""",
        "v4": """You support nonconformity and corrective action handling in an ISO management system (clause 10.2). The user has decided which actions to implement. Your task is to challenge the decision constructively – not to overturn it and not to propose other actions.

Produce four parts:

1. UNCONSIDERED RISKS: What risks or side effects do the decided actions carry, including new risks they could introduce elsewhere? 2–4 concrete points.
2. CRITICAL ASSUMPTIONS: Which assumptions must hold for the actions to actually remove the root cause? 2–3 assumptions.
3. EFFECTIVENESS VERIFICATION: How and when will the organisation verify that the action was effective? Suggest 2–3 concrete pieces of evidence and a sensible time for the review.
4. MANAGEMENT SYSTEM IMPACT: Questions about what may need updating – documented information and procedures, the risk and opportunity assessment, competence and training records, other sites. Phrase them as questions.

Do not propose other actions. Do not criticise the decision. Your job is to make sure the handling is taken all the way through.
Respond in English. Use Markdown formatting, no HTML tags.""",
    },
}

# UI texts that differ from the strategic mode. Everything not listed here is
# taken from the base TEXTS in app.py.
TEXTS = {
    "fi": {
        "title": "Korjaavan toimenpiteen tuki",
        "tagline": "Tekoäly jäsentää poikkeaman – sinä vastaat korjaavasta toimenpiteestä.",
        "about_body": (
            "Tämä tila soveltaa työkalun neljää vaihetta poikkeamien ja korjaavien toimenpiteiden "
            "käsittelyyn ISO-hallintajärjestelmissä (ISO 9001, ISO 14001 ja ISO 45001, kohta 10.2):\n\n"
            "| Vaihe | Kohta 10.2 |\n|---|---|\n"
            "| 1. Poikkeaman kartoitus | Reagointi, rajaus ja tosiasioiden selvittäminen |\n"
            "| 2. Korjaavat toimenpiteet | Juurisyy ja toimenpiteet – korjaus vai korjaava toimenpide? |\n"
            "| 3. Toimenpiteiden arviointi | Valinta omilla kriteereillä |\n"
            "| 4. Vaikuttavuus | Vaikuttavuuden todentaminen ja hallintajärjestelmän päivitys |\n\n"
            "**Tekoäly ei nimeä juurisyytä eikä suosittele toimenpidettä.** Hallintajärjestelmässä "
            "analyysistä ja päätöksestä vastaa aina nimetty ihminen – sitä myös auditoija odottaa näkevänsä.\n\n"
            "Työkalu pohjautuu strategisen liiketoiminnan kehittämisen pro gradu -tutkielmaani "
            "tekoälyavusteisesta päätöksenteosta. Lähdekoodi: [GitHub]({repo})."
        ),
        "privacy": (
            "Käytä vain keksittyjä tai anonymisoituja tapauksia. Syötteet lähetetään Anthropicin "
            "Claude-rajapintaan käsiteltäviksi, eikä sovellus tallenna niitä. Organisaation oikeat "
            "poikkeamatiedot kuuluvat organisaation hyväksymään ympäristöön, eivät julkiseen demoon."
        ),
        "steps": ["Poikkeama", "Toimenpiteet", "Arviointi", "Vaikuttavuus"],
        # Step 1
        "s1_header": "Vaihe 1 – Poikkeaman kartoitus",
        "s1_caption": "Tekoäly avaa puuttuvat tosiasiat, rajauskysymykset ja mahdolliset syyalueet. Se ei nimeä juurisyytä.",
        "q_label": "Poikkeaman kuvaus",
        "q_placeholder": "Mitä tapahtui, missä ja milloin? Miten poikkeama havaittiin? Mitä välittömiä toimia on jo tehty?",
        "q_changed": "Muokkasit kuvausta. Paina Analysoi uudelleen, jos haluat käyttää uutta versiota – jatkovaiheet käyttävät analysoitua kuvausta.",
        "warn_q": "Kuvaa ensin poikkeama.",
        "spin_1": "Tekoäly kartoittaa poikkeamaa…",
        "ai_1": "Tekoälyn poikkeamakartoitus",
        "refl_label": "Oma juurisyyhypoteesisi (pakollinen ennen seuraavaa vaihetta)",
        "refl_placeholder": "Mitkä tosiasiat olet varmistanut? Mikä on mielestäsi juurisyy ja miksi (esim. 5 × miksi)?",
        # Step 2
        "s2_header": "Vaihe 2 – Korjaavat toimenpiteet",
        "s2_caption": "Sinä ehdotat toimenpiteet. Tekoäly tarkistaa, poistaako kukin juurisyyn vai korjaako vain oireen – se ei arvota eikä valitse.",
        "alt_label": "Kirjoita 2–4 toimenpide-ehdotusta (yksi per rivi)",
        "alt_placeholder": "Toimenpide A: …\nToimenpide B: …\nToimenpide C: …",
        "btn_ai2": "Pyydä tekoälyä tarkistamaan toimenpiteet",
        "warn_alt": "Kirjoita ensin toimenpide-ehdotukset.",
        "spin_2": "Tekoäly tarkistaa toimenpiteitä…",
        "ai_2": "Tekoälyn huomiot toimenpiteistä",
        "confirm_alt": "Vahvista arvioitavat toimenpiteet",
        "final_alt_label": "Arvioitavat toimenpiteet (yksi per rivi) – muokkaa tarvittaessa",
        "warn_final_alt": "Kirjoita vähintään kaksi toimenpidettä.",
        # Step 3
        "s3_header": "Vaihe 3 – Toimenpiteiden arviointi omilla kriteereilläsi",
        "s3_caption": "Sinä määrittelet kriteerit. Tekoäly täyttää arviointitaulukon – se ei painota eikä suosittele.",
        "alts_in_comparison": "Arvioitavat toimenpiteet",
        "crit_placeholder": (
            "Poistaako juurisyyn\nKustannus\nToteutusaika\nUusien riskien mahdollisuus\n"
            "Tarve päivittää dokumentoitua tietoa\nVaikutus muihin toimipisteisiin"
        ),
        "btn_table": "Tuota arviointitaulukko",
        "spin_3": "Tekoäly rakentaa arviointitaulukkoa…",
        "table": "Arviointitaulukko",
        "dec_label": "Päätä toteutettavat toimenpiteet – vastuuhenkilö, aikataulu ja perustelu",
        "dec_placeholder": "Toteutamme toimenpiteet A ja C, koska… Vastuuhenkilö: … Määräaika: …",
        "warn_dec": "Kirjoita päätös perusteluineen (vähintään 20 merkkiä).",
        # Step 4
        "s4_header": "Vaihe 4 – Vaikuttavuus ja vaikutus hallintajärjestelmään",
        "s4_caption": "Tekoäly ei kumoa päätöstäsi. Se kysyy, miten osoitat toimenpiteen toimineen ja mitä hallintajärjestelmässä pitää päivittää.",
        "your_choice": "Päätetyt toimenpiteet",
        "btn_challenge": "Tarkastele päätöstä",
        "spin_4": "Tekoäly tarkastelee päätöstä…",
        "ai_4": "Tekoälyn vaikuttavuustarkastelu",
        "done": "Käsittely valmis. Tallenna raportti poikkeaman dokumentoituna tietona.",
        # Export
        "file_prefix": "korjaava_toimenpide",
        "rep_title": "Korjaavan toimenpiteen tuki – sessioraportti",
        "rep_question": "Poikkeama",
        "rep_v1": "Vaihe 1 – Poikkeaman kartoitus",
        "rep_refl": "Juurisyyhypoteesi",
        "rep_v2": "Vaihe 2 – Arvioitavat toimenpiteet",
        "rep_crit": "Vaihe 3 – Arviointikriteerit",
        "rep_v3": "Vaihe 3 – Arviointitaulukko",
        "rep_dec": "Vaihe 4 – Päätetyt toimenpiteet",
        "rep_v4": "Vaihe 4 – Vaikuttavuustarkastelu",
    },
    "en": {
        "title": "Corrective Action Support",
        "tagline": "AI structures the nonconformity – you own the corrective action.",
        "about_body": (
            "This mode applies the tool's four steps to nonconformity and corrective action handling "
            "in ISO management systems (ISO 9001, ISO 14001 and ISO 45001, clause 10.2):\n\n"
            "| Step | Clause 10.2 |\n|---|---|\n"
            "| 1. Nonconformity mapping | React, contain and establish the facts |\n"
            "| 2. Corrective actions | Root cause and actions – correction or corrective action? |\n"
            "| 3. Evaluating the actions | Choosing on your own criteria |\n"
            "| 4. Effectiveness | Verifying effectiveness and updating the management system |\n\n"
            "**The AI never names the root cause or recommends an action.** In a management system "
            "a named person owns the analysis and the decision – which is also what an auditor "
            "expects to see.\n\n"
            "The tool builds on my master's thesis in strategic business development on "
            "AI-assisted decision-making. Source code: [GitHub]({repo})."
        ),
        "privacy": (
            "Use fictional or anonymised cases only. Inputs are sent to Anthropic's Claude API for "
            "processing and the app does not store them. An organisation's real nonconformity data "
            "belongs in the organisation's approved environment, not in a public demo."
        ),
        "steps": ["Nonconformity", "Actions", "Evaluation", "Effectiveness"],
        # Step 1
        "s1_header": "Step 1 – Nonconformity mapping",
        "s1_caption": "The AI opens up missing facts, containment questions and possible cause areas. It does not name the root cause.",
        "q_label": "Nonconformity description",
        "q_placeholder": "What happened, where and when? How was it detected? What immediate action has already been taken?",
        "q_changed": "You edited the description. Press Analyse again to use the new version – the later steps use the analysed description.",
        "warn_q": "Please describe the nonconformity first.",
        "spin_1": "The AI is mapping the nonconformity…",
        "ai_1": "AI nonconformity mapping",
        "refl_label": "Your root-cause hypothesis (required before the next step)",
        "refl_placeholder": "Which facts have you verified? What do you believe is the root cause, and why (e.g. 5 × why)?",
        # Step 2
        "s2_header": "Step 2 – Corrective actions",
        "s2_caption": "You propose the actions. The AI checks whether each one removes the root cause or only fixes the symptom – it does not evaluate or choose.",
        "alt_label": "Write 2–4 candidate actions (one per line)",
        "alt_placeholder": "Action A: …\nAction B: …\nAction C: …",
        "btn_ai2": "Ask the AI to check the actions",
        "warn_alt": "Please write your candidate actions first.",
        "spin_2": "The AI is checking the actions…",
        "ai_2": "AI notes on the actions",
        "confirm_alt": "Confirm the actions to evaluate",
        "final_alt_label": "Actions to evaluate (one per line) – edit if needed",
        "warn_final_alt": "Please write at least two actions.",
        # Step 3
        "s3_header": "Step 3 – Evaluating actions on your criteria",
        "s3_caption": "You define the criteria. The AI fills in the evaluation table – it does not weight or recommend.",
        "alts_in_comparison": "Actions being evaluated",
        "crit_placeholder": (
            "Removes the root cause\nCost\nTime to implement\nRisk of introducing new problems\n"
            "Need to update documented information\nImpact on other sites"
        ),
        "btn_table": "Build evaluation table",
        "spin_3": "The AI is building the evaluation table…",
        "table": "Evaluation table",
        "dec_label": "Decide which actions to implement – owner, deadline and reasoning",
        "dec_placeholder": "We implement actions A and C because… Owner: … Deadline: …",
        "warn_dec": "Please write your decision and reasoning (at least 20 characters).",
        # Step 4
        "s4_header": "Step 4 – Effectiveness and management system impact",
        "s4_caption": "The AI does not overturn your decision. It asks how you will show the action worked and what in the management system needs updating.",
        "your_choice": "Decided actions",
        "btn_challenge": "Review the decision",
        "spin_4": "The AI is reviewing the decision…",
        "ai_4": "AI effectiveness review",
        "done": "Handling complete. Keep the report as documented information on the nonconformity.",
        # Export
        "file_prefix": "corrective_action",
        "rep_title": "Corrective Action Support – session report",
        "rep_question": "Nonconformity",
        "rep_v1": "Step 1 – Nonconformity mapping",
        "rep_refl": "Root-cause hypothesis",
        "rep_v2": "Step 2 – Actions evaluated",
        "rep_crit": "Step 3 – Evaluation criteria",
        "rep_v3": "Step 3 – Evaluation table",
        "rep_dec": "Step 4 – Decided actions",
        "rep_v4": "Step 4 – Effectiveness review",
    },
}
