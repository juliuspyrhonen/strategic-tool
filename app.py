"""Strategic Decision Support / Strateginen päätöstuki.

A four-step Streamlit tool in which the AI widens and structures a strategic
decision but never recommends or ranks an option. The human does the choosing.
A second mode applies the same steps to ISO corrective action handling (capa.py).
"""

import html
import logging
import re
from datetime import datetime

import anthropic
import streamlit as st

import capa

logger = logging.getLogger("strategic_tool")

# --- Configuration -----------------------------------------------------------
# All values can be overridden in Streamlit secrets without touching the code.

def _secret(name, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:  # no secrets file at all (e.g. first local run)
        return default


MODEL = _secret("ANTHROPIC_MODEL", "claude-sonnet-5-5")
EFFORT = _secret("ANTHROPIC_EFFORT", "low")  # low | medium | high
MAX_TOKENS = int(_secret("MAX_TOKENS", 8000))  # covers thinking + answer
CONTACT_EMAIL = _secret("CONTACT_EMAIL", "")
REPO_URL = "https://github.com/juliuspyrhonen/strategic-tool"

LANGS = {"fi": "Suomi", "en": "English"}
MODES = {
    "strategy": {"fi": "Strateginen päätös", "en": "Strategic decision"},
    "capa": {"fi": "Korjaava toimenpide (ISO 10.2)", "en": "Corrective action (ISO 10.2)"},
}

# --- System prompts ----------------------------------------------------------

STRATEGY_PROMPTS = {
    "fi": {
        "v1": """Olet strategisen päätöksenteon tuki. Tehtäväsi on AINOASTAAN laajentaa päätöskysymystä, ei kaventaa sitä eikä suositella ratkaisuja.

Kun käyttäjä antaa päätöskysymyksen, tuota jäsennelty taustakartoitus kolmessa osassa:

1. TIETOTARPEET: Mitä tietoa tarvitaan ennen kuin tähän voi vastata? Listaa 4–6 konkreettista kysymystä.
2. OLETUKSET: Mitä kysymys olettaa? Listaa 3–5 oletusta, jotka kannattaa tarkistaa.
3. VAIHTOEHTOISET KEHYKSET: Miten tämän kysymyksen voisi muotoilla toisin? 2–3 vaihtoehtoista tapaa katsoa asiaa.

Älä suosittele ratkaisua. Älä arvota vaihtoehtoja. Tehtäväsi on avata, ei sulkea.
Vastaa suomeksi. Käytä Markdown-muotoilua, älä HTML-tageja.""",
        "v2": """Olet strategisen päätöksenteon tuki. Tehtäväsi on auttaa käyttäjää muotoilemaan päätösvaihtoehdot selkeiksi ja vertailukelpoisiksi.

Käyttäjä antaa sinulle luonnoksen vaihtoehdoistaan. Tehtäväsi:

1. Tarkista, että jokainen vaihtoehto on konkreettinen ja erillinen (ei päällekkäinen toisen kanssa).
2. Ehdota tarkennuksia, jos vaihtoehto on epämääräinen.
3. Nosta esiin, jos jokin tärkeä vaihtoehto puuttuu kokonaan.

Älä arvota vaihtoehtoja. Älä suosittele, mikä on paras. Älä järjestä niitä paremmuusjärjestykseen.
Tehtäväsi on ainoastaan auttaa muotoilemaan vaihtoehdot niin selkeiksi, että niitä voi vertailla.
Vastaa suomeksi. Käytä Markdown-muotoilua, älä HTML-tageja.""",
        "v3": """Olet strategisen päätöksenteon tuki. Tehtäväsi on täyttää vertailutaulukko käyttäjän määrittelemillä kriteereillä.

Saat päätöskysymyksen, vaihtoehdot ja käyttäjän määrittelemät kriteerit. Tuota niiden pohjalta selkeä vertailutaulukko Markdown-muodossa.

Säännöt:
1. Täytä taulukko jokaiselle vaihtoehdolle ja kriteerille. Käytä lyhyttä, konkreettista arviota (2–4 lausetta per solu).
2. ÄLÄ painota kriteerejä. Kaikki kriteerit ovat yhtä tärkeitä – painotus on käyttäjän tehtävä.
3. ÄLÄ suosittele vaihtoehtoa. Älä käytä sanoja kuten paras, suositeltava tai selvästi parempi.
4. Jos tietoa ei ole riittävästi arviointiin, kirjoita "Vaatii lisäselvitystä" sen sijaan, että arvaat.
5. Taulukon jälkeen listaa lyhyesti 2–3 asiaa, joita taulukko ei pysty kuvaamaan.
6. Älä käytä HTML-tageja tai rivinvaihtoja taulukon soluissa.

Muoto (yksi sarake per vaihtoehto):
| Kriteeri | Vaihtoehto A | Vaihtoehto B |
|---|---|---|
| Kriteeri 1 | ... | ... |

Vastaa suomeksi.""",
        "v4": """Olet strategisen päätöksenteon tuki. Käyttäjä on tehnyt valintansa. Tehtäväsi on kyseenalaistaa se rakentavasti – ei kumota sitä eikä suositella toista vaihtoehtoa.

Tuota kolmessa osassa:

1. HARKITSEMATTOMAT RISKIT: Mitä riskejä tai sivuvaikutuksia valintaan liittyy, joita vertailutaulukko ei välttämättä näyttänyt? Listaa 2–4 konkreettista asiaa.
2. KRIITTISET OLETUKSET: Minkä oletusten pitää pitää paikkansa, jotta valinta toimii? Listaa 2–3 oletusta.
3. TARKISTUSPISTEET: Miten käyttäjä tietää 3–6 kuukauden kuluttua, oliko valinta oikea? Ehdota 2–3 konkreettista mittaria tai merkkiä.

Älä ehdota toista vaihtoehtoa. Älä arvostele valintaa. Tehtäväsi on varmistaa, että käyttäjä on miettinyt sen loppuun asti.
Vastaa suomeksi. Käytä Markdown-muotoilua, älä HTML-tageja.""",
    },
    "en": {
        "v1": """You are a strategic decision-support assistant. Your ONLY task is to widen the decision question – not to narrow it and not to recommend solutions.

When the user gives you a decision question, produce a structured background mapping in three parts:

1. INFORMATION NEEDS: What information is needed before this question can be answered? List 4–6 concrete questions.
2. ASSUMPTIONS: What does the question assume? List 3–5 assumptions worth checking.
3. ALTERNATIVE FRAMINGS: How else could this question be framed? Give 2–3 alternative ways of looking at it.

Do not recommend a solution. Do not evaluate options. Your job is to open up, not to close down.
Respond in English. Use Markdown formatting, no HTML tags.""",
        "v2": """You are a strategic decision-support assistant. Your task is to help the user formulate their decision alternatives so that they are clear and comparable.

The user gives you a draft of their alternatives. Your task:

1. Check that each alternative is concrete and distinct (does not overlap with another).
2. Suggest refinements if an alternative is vague.
3. Point out if an important alternative seems to be missing entirely.

Do not evaluate the alternatives. Do not say which is best. Do not rank them.
Your only job is to help formulate the alternatives clearly enough that they can be compared.
Respond in English. Use Markdown formatting, no HTML tags.""",
        "v3": """You are a strategic decision-support assistant. Your task is to fill in a comparison table using the criteria defined by the user.

You receive the decision question, the alternatives and the user's criteria. Based on these, produce a clear comparison table in Markdown.

Rules:
1. Fill in the table for every alternative and criterion. Use a short, concrete assessment (2–4 sentences per cell).
2. DO NOT weight the criteria. All criteria are equally important – weighting is the user's job.
3. DO NOT recommend an alternative. Do not use words such as best, recommended or clearly better.
4. If there is not enough information for an assessment, write "Requires further investigation" instead of guessing.
5. After the table, briefly list 2–3 things the table cannot capture.
6. Do not use HTML tags or line breaks inside table cells.

Format (one column per alternative):
| Criterion | Alternative A | Alternative B |
|---|---|---|
| Criterion 1 | ... | ... |

Respond in English.""",
        "v4": """You are a strategic decision-support assistant. The user has made their choice. Your task is to challenge it constructively – not to overturn it and not to recommend another alternative.

Produce three parts:

1. UNCONSIDERED RISKS: What risks or side effects does the choice carry that the comparison table may not have shown? List 2–4 concrete points.
2. CRITICAL ASSUMPTIONS: Which assumptions must hold for this choice to work? List 2–3 assumptions.
3. CHECKPOINTS: How will the user know in 3–6 months whether the choice was right? Suggest 2–3 concrete metrics or signals.

Do not suggest another alternative. Do not criticise the choice. Your job is to make sure the user has thought it through.
Respond in English. Use Markdown formatting, no HTML tags.""",
    },
}

PROMPTS = {"strategy": STRATEGY_PROMPTS, "capa": capa.PROMPTS}
MODE_TEXTS = {"capa": capa.TEXTS}  # overrides on top of the base TEXTS below

# --- UI texts ----------------------------------------------------------------

TEXTS = {
    "fi": {
        "title": "Strateginen päätöstuki",
        "tagline": "Tekoäly avaa päätöksen – sinä teet sen.",
        "about_title": "Mikä tämä työkalu on?",
        "about_body": (
            "Työkalu ohjaa strategisen päätöksen neljän vaiheen läpi: taustakartoitus, "
            "vaihtoehtojen muotoilu, kriteeripohjainen vertailu ja valinnan kyseenalaistaminen.\n\n"
            "**Tekoäly ei missään vaiheessa suosittele ratkaisua eikä aseta vaihtoehtoja "
            "järjestykseen.** Se on tietoinen suunnitteluratkaisu: tekoäly laajentaa ja jäsentää, "
            "mutta kontekstin tulkinta, kriteerien painotus ja valinta jäävät ihmiselle. "
            "Vaiheiden välissä kirjoitat oman reflektiosi ennen kuin pääset eteenpäin.\n\n"
            "Työkalu pohjautuu strategisen liiketoiminnan kehittämisen pro gradu -tutkielmaani "
            "tekoälyavusteisesta päätöksenteosta. Lähdekoodi: [GitHub]({repo})."
        ),
        "privacy": (
            "Älä syötä luottamuksellisia tietoja tai henkilötietoja. Syötteet lähetetään "
            "Anthropicin Claude-rajapintaan käsiteltäviksi. Sovellus ei tallenna niitä – "
            "istunto katoaa, kun suljet sivun."
        ),
        "lang_label": "Kieli / Language",
        "mode_label": "Työkalun tila",
        "progress": "Eteneminen",
        "steps": ["Taustakartoitus", "Vaihtoehdot", "Vertailu", "Kyseenalaistus"],
        "reset": "Aloita alusta",
        "model": "Malli",
        # Step 1
        "s1_header": "Vaihe 1 – Taustakartoitus",
        "s1_caption": "Tekoäly laajentaa kysymyksesi tietotarpeiksi, oletuksiksi ja vaihtoehtoisiksi kehyksiksi. Se ei suosittele ratkaisua.",
        "q_label": "Päätöskysymys",
        "q_placeholder": "esim. Pitäisikö meidän laajentaa palveluliiketoimintaa Saksan markkinoille ensi vuonna?",
        "q_changed": "Muokkasit kysymystä. Paina Analysoi uudelleen, jos haluat käyttää uutta versiota – jatkovaiheet käyttävät analysoitua kysymystä.",
        "btn_analyze": "Analysoi",
        "warn_q": "Kirjoita ensin päätöskysymys.",
        "spin_1": "Tekoäly kartoittaa tietotarpeita…",
        "ai_1": "Tekoälyn taustakartoitus",
        "your_turn": "Sinun vuorosi",
        "refl_label": "Oma reflektio (pakollinen ennen seuraavaa vaihetta)",
        "refl_placeholder": "Mitkä tietotarpeet ovat oikeasti kriittisiä? Mitkä oletukset pitävät? Mikä kehys sopii parhaiten kontekstiisi?",
        "btn_to2": "Siirry vaiheeseen 2",
        "warn_refl": "Kirjoita reflektioon vähintään 20 merkkiä.",
        # Step 2
        "s2_header": "Vaihe 2 – Vaihtoehtojen muotoilu",
        "s2_caption": "Sinä muotoilet vaihtoehdot. Tekoäly tarkistaa, että ne ovat konkreettisia ja erillisiä – se ei arvota eikä valitse.",
        "alt_label": "Kirjoita 2–4 vaihtoehtoa (yksi per rivi)",
        "alt_placeholder": "Vaihtoehto A: Perustetaan oma myyntiyhtiö Saksaan\nVaihtoehto B: Laajennetaan jälleenmyyjäverkoston kautta\nVaihtoehto C: Ei laajennusta tänä vuonna",
        "btn_ai2": "Pyydä tekoälyltä muotoiluapua",
        "warn_alt": "Kirjoita ensin vaihtoehdot.",
        "spin_2": "Tekoäly tarkistaa vaihtoehtojen muotoilun…",
        "ai_2": "Tekoälyn huomiot vaihtoehtojen muotoilusta",
        "confirm_alt": "Vahvista lopulliset vaihtoehdot",
        "final_alt_label": "Lopulliset vaihtoehdot (yksi per rivi) – muokkaa tarvittaessa",
        "btn_to3": "Siirry vaiheeseen 3",
        "warn_final_alt": "Kirjoita vähintään kaksi vaihtoehtoa.",
        # Step 3
        "s3_header": "Vaihe 3 – Vertailu omilla kriteereilläsi",
        "s3_caption": "Sinä määrittelet kriteerit. Tekoäly täyttää vertailutaulukon – se ei painota eikä suosittele.",
        "alts_in_comparison": "Vaihtoehdot vertailussa",
        "crit_label": "Määrittele vertailukriteerit (yksi per rivi)",
        "crit_placeholder": "Taloudellinen riski\nHenkilöstön kuormitus\nVaikutus asiakassuhteisiin\nToteutusaikataulu",
        "btn_table": "Tuota vertailutaulukko",
        "warn_crit": "Kirjoita ensin kriteerit.",
        "spin_3": "Tekoäly rakentaa vertailutaulukkoa…",
        "table": "Vertailutaulukko",
        "dec_label": "Tee valintasi ja perustele se lyhyesti",
        "dec_placeholder": "Valitsen vaihtoehdon X, koska…",
        "btn_to4": "Siirry vaiheeseen 4",
        "warn_dec": "Kirjoita valintasi perusteluineen (vähintään 20 merkkiä).",
        # Step 4
        "s4_header": "Vaihe 4 – Valinnan kyseenalaistaminen",
        "s4_caption": "Tekoäly ei kumoa valintaasi eikä suosittele toista. Se kysyy, mitä et ehkä ole harkinnut.",
        "your_choice": "Valintasi",
        "btn_challenge": "Kyseenalaista valinta",
        "spin_4": "Tekoäly tarkastelee valintaasi kriittisesti…",
        "ai_4": "Tekoälyn kriittinen tarkastelu",
        "done": "Prosessi valmis.",
        # Export
        "dl_header": "Lataa sessioraportti",
        "dl_txt": "Lataa tekstitiedostona (.txt)",
        "dl_html": "Lataa HTML-raporttina (.html)",
        "dl_caption": "HTML-tiedoston voi avata selaimessa ja tulostaa PDF:ksi (Ctrl+P).",
        "file_prefix": "paatossessio",
        "rep_title": "Strateginen päätöstuki – sessioraportti",
        "rep_created": "Luotu",
        "rep_question": "Päätöskysymys",
        "rep_v1": "Vaihe 1 – Taustakartoitus",
        "rep_refl": "Oma reflektio",
        "rep_v2": "Vaihe 2 – Vahvistetut vaihtoehdot",
        "rep_crit": "Vaihe 3 – Vertailukriteerit",
        "rep_v3": "Vaihe 3 – Vertailutaulukko",
        "rep_dec": "Vaihe 4 – Oma valinta",
        "rep_v4": "Vaihe 4 – Tekoälyn kriittinen tarkastelu",
        # Errors
        "err_config": "Sovelluksen API-asetukset puuttuvat tai ovat virheelliset.",
        "err_limit": "Demon käyttöraja on täynnä tältä kuukaudelta.",
        "err_busy": "Tekoälypalvelu on juuri nyt ruuhkautunut. Yritä hetken kuluttua uudelleen.",
        "err_network": "Yhteys tekoälypalveluun epäonnistui. Yritä hetken kuluttua uudelleen.",
        "err_generic": "Tekoälykutsu epäonnistui. Yritä uudelleen.",
        "err_empty": "Tekoäly palautti tyhjän vastauksen. Yritä uudelleen.",
        "err_contact": "Ota yhteyttä: {email}",
        "truncated": "_(Vastaus katkesi pituusrajaan.)_",
    },
    "en": {
        "title": "Strategic Decision Support",
        "tagline": "AI opens up the decision – you make it.",
        "about_title": "What is this tool?",
        "about_body": (
            "The tool guides a strategic decision through four steps: background mapping, "
            "formulating alternatives, criteria-based comparison and challenging the choice.\n\n"
            "**At no point does the AI recommend a solution or rank the alternatives.** "
            "This is a deliberate design choice: the AI widens and structures, but interpreting "
            "the context, weighting the criteria and making the choice stay with the human. "
            "Between steps you write your own reflection before you can move on.\n\n"
            "The tool builds on my master's thesis in strategic business development on "
            "AI-assisted decision-making. Source code: [GitHub]({repo})."
        ),
        "privacy": (
            "Please do not enter confidential or personal data. Inputs are sent to Anthropic's "
            "Claude API for processing. The app does not store them – the session is gone "
            "when you close the page."
        ),
        "lang_label": "Kieli / Language",
        "mode_label": "Mode",
        "progress": "Progress",
        "steps": ["Background mapping", "Alternatives", "Comparison", "Challenge"],
        "reset": "Start over",
        "model": "Model",
        # Step 1
        "s1_header": "Step 1 – Background mapping",
        "s1_caption": "The AI widens your question into information needs, assumptions and alternative framings. It does not recommend a solution.",
        "q_label": "Decision question",
        "q_placeholder": "e.g. Should we expand our service business into the German market next year?",
        "q_changed": "You edited the question. Press Analyse again to use the new version – the later steps use the analysed question.",
        "btn_analyze": "Analyse",
        "warn_q": "Please enter a decision question first.",
        "spin_1": "The AI is mapping information needs…",
        "ai_1": "AI background mapping",
        "your_turn": "Your turn",
        "refl_label": "Your reflection (required before the next step)",
        "refl_placeholder": "Which information needs are truly critical? Which assumptions hold? Which framing fits your context best?",
        "btn_to2": "Continue to step 2",
        "warn_refl": "Please write at least 20 characters of reflection.",
        # Step 2
        "s2_header": "Step 2 – Formulating alternatives",
        "s2_caption": "You formulate the alternatives. The AI checks that they are concrete and distinct – it does not evaluate or choose.",
        "alt_label": "Write 2–4 alternatives (one per line)",
        "alt_placeholder": "Alternative A: Set up our own sales company in Germany\nAlternative B: Expand through the distributor network\nAlternative C: No expansion this year",
        "btn_ai2": "Ask the AI for formulation help",
        "warn_alt": "Please write your alternatives first.",
        "spin_2": "The AI is checking how the alternatives are formulated…",
        "ai_2": "AI notes on the alternatives",
        "confirm_alt": "Confirm the final alternatives",
        "final_alt_label": "Final alternatives (one per line) – edit if needed",
        "btn_to3": "Continue to step 3",
        "warn_final_alt": "Please write at least two alternatives.",
        # Step 3
        "s3_header": "Step 3 – Comparison on your criteria",
        "s3_caption": "You define the criteria. The AI fills in the comparison table – it does not weight or recommend.",
        "alts_in_comparison": "Alternatives being compared",
        "crit_label": "Define the comparison criteria (one per line)",
        "crit_placeholder": "Financial risk\nWorkload on staff\nImpact on customer relationships\nImplementation timeline",
        "btn_table": "Build comparison table",
        "warn_crit": "Please write your criteria first.",
        "spin_3": "The AI is building the comparison table…",
        "table": "Comparison table",
        "dec_label": "Make your choice and briefly justify it",
        "dec_placeholder": "I choose alternative X because…",
        "btn_to4": "Continue to step 4",
        "warn_dec": "Please write your choice and reasoning (at least 20 characters).",
        # Step 4
        "s4_header": "Step 4 – Challenging the choice",
        "s4_caption": "The AI does not overturn your choice or recommend another. It asks what you may not have considered.",
        "your_choice": "Your choice",
        "btn_challenge": "Challenge my choice",
        "spin_4": "The AI is examining your choice critically…",
        "ai_4": "AI critical review",
        "done": "Process complete.",
        # Export
        "dl_header": "Download session report",
        "dl_txt": "Download as text (.txt)",
        "dl_html": "Download as HTML report (.html)",
        "dl_caption": "Open the HTML file in a browser and print it to PDF (Ctrl+P).",
        "file_prefix": "decision_session",
        "rep_title": "Strategic Decision Support – session report",
        "rep_created": "Created",
        "rep_question": "Decision question",
        "rep_v1": "Step 1 – Background mapping",
        "rep_refl": "Own reflection",
        "rep_v2": "Step 2 – Confirmed alternatives",
        "rep_crit": "Step 3 – Comparison criteria",
        "rep_v3": "Step 3 – Comparison table",
        "rep_dec": "Step 4 – Own choice",
        "rep_v4": "Step 4 – AI critical review",
        # Errors
        "err_config": "The app's API settings are missing or invalid.",
        "err_limit": "The demo's usage limit for this month has been reached.",
        "err_busy": "The AI service is busy right now. Please try again in a moment.",
        "err_network": "Could not reach the AI service. Please try again in a moment.",
        "err_generic": "The AI call failed. Please try again.",
        "err_empty": "The AI returned an empty response. Please try again.",
        "err_contact": "Contact: {email}",
        "truncated": "_(The response was cut off at the length limit.)_",
    },
}

# Session-state keys: workflow results and input widgets
STATE_KEYS = [
    "question", "v1_output", "v1_reflection", "v2_output", "v2_alternatives",
    "criteria", "v3_output", "final_decision", "v4_output",
]
INPUT_KEYS = ["in_question", "in_reflection", "in_alts", "in_final_alts", "in_criteria", "in_decision"]

# Keys cleared when an earlier step is re-run, so later steps never show stale results
DOWNSTREAM = {
    1: ["v1_reflection", "v2_output", "v2_alternatives", "criteria", "v3_output", "final_decision", "v4_output"],
    2: ["v2_alternatives", "criteria", "v3_output", "final_decision", "v4_output"],
    3: ["criteria", "v3_output", "final_decision", "v4_output"],
    4: ["final_decision", "v4_output"],
}


# --- Helpers -----------------------------------------------------------------

def reset_session():
    for key in STATE_KEYS:
        st.session_state[key] = None
    for key in INPUT_KEYS:
        st.session_state.pop(key, None)


def clear(keys):
    for key in keys:
        st.session_state[key] = None


def on_lang_change():
    st.query_params["lang"] = st.session_state.lang_choice
    reset_session()


def on_mode_change():
    st.query_params["mode"] = st.session_state.mode_choice
    reset_session()


def clean_md(text):
    """Remove stray HTML line breaks the model might put in table cells."""
    return re.sub(r"<br\s*/?>", " ", text or "", flags=re.IGNORECASE)


@st.cache_resource
def get_client():
    api_key = _secret("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key, max_retries=3, timeout=180)


def call_claude(system_prompt, user_message, t):
    """Call the API. Returns the answer text, or None after showing a friendly error."""
    client = get_client()
    contact = f" {t['err_contact'].format(email=CONTACT_EMAIL)}" if CONTACT_EMAIL else ""
    if client is None:
        st.error(t["err_config"] + contact)
        return None
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            output_config={"effort": EFFORT},
        )
    except anthropic.AuthenticationError:
        logger.exception("Authentication failed")
        st.error(t["err_config"] + contact)
        return None
    except (anthropic.RateLimitError, anthropic.OverloadedError, anthropic.InternalServerError):
        logger.exception("API busy")
        st.error(t["err_busy"])
        return None
    except (anthropic.APIConnectionError, anthropic.APITimeoutError):
        logger.exception("API connection problem")
        st.error(t["err_network"])
        return None
    except anthropic.BadRequestError as e:
        logger.exception("Bad request")
        if "usage limit" in str(e).lower():
            st.error(t["err_limit"] + contact)
        else:
            st.error(t["err_generic"] + contact)
        return None
    except Exception:
        logger.exception("Unexpected API error")
        st.error(t["err_generic"] + contact)
        return None

    # Newer models may return thinking blocks before the text: pick text blocks only
    text = "".join(b.text for b in message.content if getattr(b, "type", "") == "text").strip()
    if not text:
        st.error(t["err_empty"])
        return None
    if message.stop_reason == "max_tokens":
        text += "\n\n" + t["truncated"]
    return clean_md(text)


def as_bullets(lines_text):
    lines = [ln.strip() for ln in lines_text.splitlines() if ln.strip()]
    return "\n".join(f"- {ln}" for ln in lines)


def count_lines(text):
    return len([ln for ln in (text or "").splitlines() if ln.strip()])


def current_step():
    s = st.session_state
    if s.v4_output:
        return 5
    if s.final_decision:
        return 4
    if s.v2_alternatives:
        return 3
    if s.v1_reflection:
        return 2
    return 1


# --- Export ------------------------------------------------------------------

def report_sections(t):
    s = st.session_state
    return [
        (t["rep_v1"], s.v1_output, "md"),
        (t["rep_refl"], s.v1_reflection, "text"),
        (t["rep_v2"], s.v2_alternatives, "text"),
        (t["rep_crit"], s.criteria, "text"),
        (t["rep_v3"], s.v3_output, "md"),
        (t["rep_dec"], s.final_decision, "text"),
        (t["rep_v4"], s.v4_output, "md"),
    ]


def build_text_export(t, timestamp):
    lines = [t["rep_title"].upper(), f"{t['rep_created']}: {timestamp}", "=" * 60, "",
             t["rep_question"].upper(), st.session_state.question or "", ""]
    for title, content, _ in report_sections(t):
        if content:
            lines += ["=" * 60, title.upper(), content, ""]
    return "\n".join(lines)


def _inline(text):
    escaped = html.escape(text.strip())
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<![\w*])_(.+?)_(?![\w*])", r"<em>\1</em>", escaped)
    return escaped


def md_to_html(text):
    """Minimal, escaped Markdown → HTML for tables, headings, lists and paragraphs."""
    out, in_table, in_list, header_row = [], False, False, False
    for raw in clean_md(text).splitlines():
        line = raw.strip()
        is_row = line.startswith("|")
        bullet = re.match(r"^[-*] (.+)$", line)
        if in_table and not is_row:
            out.append("</table>")
            in_table = False
        if in_list and not bullet:
            out.append("</ul>")
            in_list = False
        if is_row:
            if re.match(r"^\|[\s:\-|]+\|$", line):
                continue
            if not in_table:
                out.append("<table>")
                in_table, header_row = True, True
            tag = "th" if header_row else "td"
            header_row = False
            cells = [c for c in line.strip("|").split("|")]
            out.append("<tr>" + "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells) + "</tr>")
        elif bullet:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(bullet.group(1))}</li>")
        elif (m := re.match(r"^(#{1,4}) (.+)$", line)):
            level = min(len(m.group(1)) + 2, 6)
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
        elif line:
            out.append(f"<p>{_inline(line)}</p>")
    if in_table:
        out.append("</table>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def text_to_html(text):
    return "".join(f"<p>{html.escape(ln)}</p>" for ln in text.splitlines() if ln.strip())


def build_html_export(t, timestamp, lang):
    body = []
    for title, content, kind in report_sections(t):
        if content:
            rendered = md_to_html(content) if kind == "md" else text_to_html(content)
            body.append(f"<h2>{html.escape(title)}</h2>\n{rendered}")
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<title>{html.escape(t['rep_title'])} – {timestamp}</title>
<style>
  body {{ font-family: Georgia, serif; max-width: 900px; margin: 40px auto; padding: 0 20px; color: #222; line-height: 1.5; }}
  h1 {{ font-size: 1.6em; border-bottom: 2px solid #333; padding-bottom: 8px; }}
  h2 {{ font-size: 1.2em; margin-top: 32px; color: #444; border-left: 4px solid #888; padding-left: 10px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
  th, td {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; font-size: 0.9em; text-align: left; }}
  th {{ background: #f2f2f2; }}
  .meta {{ color: #888; font-size: 0.9em; }}
  @media print {{ body {{ margin: 20px; }} }}
</style>
</head>
<body>
<h1>{html.escape(t['rep_title'])}</h1>
<p class="meta">{html.escape(t['rep_created'])}: {timestamp}</p>
<h2>{html.escape(t['rep_question'])}</h2>
<p><strong>{html.escape(st.session_state.question or '')}</strong></p>
{chr(10).join(body)}
</body>
</html>"""


# --- App ---------------------------------------------------------------------

if "lang_choice" not in st.session_state:
    initial = st.query_params.get("lang", "fi")
    st.session_state.lang_choice = initial if initial in LANGS else "fi"
lang = st.session_state.lang_choice
if "mode_choice" not in st.session_state:
    initial_mode = st.query_params.get("mode", "strategy")
    st.session_state.mode_choice = initial_mode if initial_mode in MODES else "strategy"
mode = st.session_state.mode_choice
t = {**TEXTS[lang], **MODE_TEXTS.get(mode, {}).get(lang, {})}
P = PROMPTS[mode][lang]

st.set_page_config(page_title=t["title"], page_icon="🧭", layout="centered")

for key in STATE_KEYS:
    st.session_state.setdefault(key, None)
s = st.session_state

# Sidebar: language, progress, reset
with st.sidebar:
    st.radio(t["lang_label"], options=list(LANGS), format_func=LANGS.get,
             key="lang_choice", on_change=on_lang_change, horizontal=True)
    st.radio(t["mode_label"], options=list(MODES), format_func=lambda m: MODES[m][lang],
             key="mode_choice", on_change=on_mode_change)
    st.divider()
    st.subheader(t["progress"])
    step = current_step()
    st.progress(min(step - 1, 4) / 4)
    for i, name in enumerate(t["steps"], start=1):
        mark = "✅" if i < step else ("➡️" if i == step else "⬜")
        st.markdown(f"{mark} {i}. {name}")
    st.divider()
    st.button(t["reset"], on_click=reset_session, width="stretch")
    st.caption(f"{t['model']}: `{MODEL}`")

st.title(t["title"])
st.markdown(f"*{t['tagline']}*")
with st.expander(t["about_title"]):
    st.markdown(t["about_body"].format(repo=REPO_URL))
st.info(t["privacy"], icon="🔒")

# STEP 1
st.header(t["s1_header"])
st.caption(t["s1_caption"])
question_input = st.text_area(t["q_label"], key="in_question", placeholder=t["q_placeholder"],
                              height=100, max_chars=1500)

if st.button(t["btn_analyze"], type="primary"):
    if not question_input.strip():
        st.warning(t["warn_q"])
    else:
        with st.spinner(t["spin_1"]):
            result = call_claude(P["v1"], question_input.strip(), t)
        if result:
            s.question = question_input.strip()
            s.v1_output = result
            clear(DOWNSTREAM[1])

if s.v1_output:
    if question_input.strip() and question_input.strip() != s.question:
        st.caption(f"⚠️ {t['q_changed']}")
    st.divider()
    st.subheader(t["ai_1"])
    st.markdown(s.v1_output)
    st.divider()
    st.subheader(t["your_turn"])
    reflection = st.text_area(t["refl_label"], key="in_reflection", height=150,
                              placeholder=t["refl_placeholder"], max_chars=3000)
    if st.button(t["btn_to2"]):
        if len(reflection.strip()) < 20:
            st.warning(t["warn_refl"])
        else:
            s.v1_reflection = reflection.strip()
            clear(DOWNSTREAM[2])
            st.rerun()

# STEP 2
if s.v1_reflection:
    st.divider()
    st.header(t["s2_header"])
    st.caption(t["s2_caption"])
    alternatives_draft = st.text_area(t["alt_label"], key="in_alts", height=150,
                                      placeholder=t["alt_placeholder"], max_chars=2000)

    if st.button(t["btn_ai2"], type="primary"):
        if not alternatives_draft.strip():
            st.warning(t["warn_alt"])
        else:
            user_msg = (
                f"{t['rep_question']}: {s.question}\n\n"
                f"{t['rep_refl']}: {s.v1_reflection}\n\n"
                f"{t['alt_label']}:\n{alternatives_draft.strip()}"
            )
            with st.spinner(t["spin_2"]):
                result = call_claude(P["v2"], user_msg, t)
            if result:
                s.v2_output = result
                st.session_state["in_final_alts"] = alternatives_draft.strip()
                clear(DOWNSTREAM[2])

    if s.v2_output:
        st.divider()
        st.subheader(t["ai_2"])
        st.markdown(s.v2_output)
        st.divider()
        st.subheader(t["confirm_alt"])
        final_alternatives = st.text_area(t["final_alt_label"], key="in_final_alts",
                                          height=150, max_chars=2000)
        if st.button(t["btn_to3"]):
            if count_lines(final_alternatives) < 2:
                st.warning(t["warn_final_alt"])
            else:
                s.v2_alternatives = final_alternatives.strip()
                clear(DOWNSTREAM[3])
                st.rerun()

# STEP 3
if s.v2_alternatives:
    st.divider()
    st.header(t["s3_header"])
    st.caption(t["s3_caption"])
    st.markdown(f"**{t['alts_in_comparison']}:**")
    st.markdown(as_bullets(s.v2_alternatives))
    criteria = st.text_area(t["crit_label"], key="in_criteria", height=150,
                            placeholder=t["crit_placeholder"], max_chars=1500)

    if st.button(t["btn_table"], type="primary"):
        if not criteria.strip():
            st.warning(t["warn_crit"])
        else:
            user_msg = (
                f"{t['rep_question']}: {s.question}\n\n"
                f"{t['alts_in_comparison']}:\n{s.v2_alternatives}\n\n"
                f"{t['crit_label']}:\n{criteria.strip()}"
            )
            with st.spinner(t["spin_3"]):
                result = call_claude(P["v3"], user_msg, t)
            if result:
                s.criteria = criteria.strip()
                s.v3_output = result
                clear(DOWNSTREAM[4])

    if s.v3_output:
        st.divider()
        st.subheader(t["table"])
        st.markdown(s.v3_output)
        st.divider()
        decision = st.text_area(t["dec_label"], key="in_decision", height=120,
                                placeholder=t["dec_placeholder"], max_chars=2000)
        if st.button(t["btn_to4"]):
            if len(decision.strip()) < 20:
                st.warning(t["warn_dec"])
            else:
                s.final_decision = decision.strip()
                s.v4_output = None
                st.rerun()

# STEP 4
if s.final_decision:
    st.divider()
    st.header(t["s4_header"])
    st.caption(t["s4_caption"])
    st.markdown(f"**{t['your_choice']}:**")
    st.text(s.final_decision)

    if st.button(t["btn_challenge"], type="primary"):
        user_msg = (
            f"{t['rep_question']}: {s.question}\n\n"
            f"{t['alts_in_comparison']}:\n{s.v2_alternatives}\n\n"
            f"{t['table']}:\n{s.v3_output}\n\n"
            f"{t['your_choice']}:\n{s.final_decision}"
        )
        with st.spinner(t["spin_4"]):
            result = call_claude(P["v4"], user_msg, t)
        if result:
            s.v4_output = result
            st.rerun()

    if s.v4_output:
        st.divider()
        st.subheader(t["ai_4"])
        st.markdown(s.v4_output)
        st.divider()
        st.success(t["done"])

        st.subheader(t["dl_header"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        stamp = datetime.now().strftime("%Y%m%d_%H%M")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(t["dl_txt"], data=build_text_export(t, timestamp).encode("utf-8"),
                               file_name=f"{t['file_prefix']}_{stamp}.txt", mime="text/plain")
        with col2:
            st.download_button(t["dl_html"], data=build_html_export(t, timestamp, lang).encode("utf-8"),
                               file_name=f"{t['file_prefix']}_{stamp}.html", mime="text/html")
        st.caption(t["dl_caption"])
