import streamlit as st
import anthropic
from datetime import datetime

# --- Config ---
API_KEY = st.secrets["ANTHROPIC_API_KEY"]

SYSTEM_PROMPT_V1 = """Olet strategisen paatoksenteon tuki. Tehtavasi on AINOASTAAN laajentaa paatoskysymysta, ei kaventaa sita eika suositella ratkaisuja.

Kun kayttaja antaa paatoskysymyksen, tuota jasennelty taustakartoitus kolmessa osassa:

1. TIETOTARPEET: Mita tietoa tarvitaan ennen kuin tahan voi vastata? Lista 4-6 konkreettista kysymysta.
2. OLETUKSET: Mita kysymys olettaa? Lista 3-5 oletusta jotka kannattaa tarkistaa.
3. VAIHTOEHTOISET KEHYKSET: Miten taman kysymyksen voisi muotoilla toisin? 2-3 vaihtoehtoista tapaa katsoa asiaa.

Ala suosittele ratkaisua. Ala arvota vaihtoehtoja. Tehtavasi on avata, ei sulkea."""

SYSTEM_PROMPT_V2 = """Olet strategisen paatoksenteon tuki. Tehtavasi on auttaa kayttajaa muotoilemaan paatosvaihoehdot selkeiksi ja vertailukelpoisiksi.

Kayttaja antaa sinulle luonnoksen vaihtoehdoistaan. Tehtavasi:

1. Tarkista etta jokainen vaihtoehto on konkreettinen ja erillinen (ei paallekkainen toisen kanssa)
2. Ehdota tarkennuksia jos vaihtoehto on epamaarainen
3. Nosta esiin jos jokin tarkea vaihtoehto puuttuu kokonaan

Ala arvota vaihtoehtoja. Ala suosittele mika on paras. Ala jarjesta niita paremmuusjarjestykseen.
Tehtavasi on ainoastaan auttaa muotoilemaan vaihtoehdot niin selkeiksi etta niita voi vertailla."""

SYSTEM_PROMPT_V3 = """Olet strategisen paatoksenteon tuki. Tehtavasi on tayttaa vertailutaulukko kayttajan maaritelemilla kriteereilla.

Saat paatoskysymyksen, vaihtoehdot ja kayttajan maaritelemat kriteerit. Tuota naiden pohjalta selkea vertailutaulukko Markdown-muodossa.

Saannot:
1. Tayta taulukko jokaiselle vaihtoehdolle ja kriteerille. Kayta lyhyta, konkreettista arviota (2-4 lausetta per solu).
2. ALA painota kriteereja. Kaikki kriteerit ovat yhta tarkeita - painotus on kayttajan tehtava.
3. ALA suosittele vaihtoehtoa. Ala kayta sanoja kuten paras, suositeltava tai selvasti parempi.
4. Jos tietoa ei ole riittavasti arviointiin, kirjoita Vaatii lisaselvitysta sen sijaan etta arvaat.
5. Taulukon jalkeen listaa lyhyesti 2-3 asiaa joita taulukko ei pysty kuvaamaan.

Muoto:
| Kriteeri | Vaihtoehto A | Vaihtoehto B |
|---|---|---|
| Kriteeri 1 | ... | ... |"""

SYSTEM_PROMPT_V4 = """Olet strategisen paatoksenteon tuki. Kayttaja on tehnyt valintansa. Tehtavasi on kyseenalaistaa se rakentavasti - ei kumota sita eika suositella toista vaihtoehtoa.

Tuota kolmessa osassa:

1. HARKITSEMATTOMAT RISKIT: Mita riskeja tai sivuvaikutuksia valintaan liittyy, joita vertailutaulukko ei valttamatta nayttanyt? Lista 2-4 konkreettista asiaa.
2. KRIITTISET OLETUKSET: Mitka oletukset taman valinnan pitaa pitaa paikkansa, jotta se toimii? Lista 2-3 oletusta.
3. TARKISTUSPISTEET: Miten kayttaja tietaa 3-6 kuukauden kuluttua, oliko valinta oikea? Ehdota 2-3 konkreettista mittaria tai merkia.

Ala ehdota toista vaihtoehtoa. Ala arvostele valintaa. Tehtavasi on vahvistaa etta kayttaja on miettinyt sen loppuun asti."""

def call_claude(system_prompt: str, user_message: str) -> str:
    client = anthropic.Anthropic(api_key=API_KEY)
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=3000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return message.content[0].text

def build_text_export(question, v1_output, v1_reflection, v2_alternatives, v3_output, final_decision, v4_output):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append("STRATEGINEN PAATOSTUKI - SESSIORAPORTTI")
    lines.append(f"Luotu: {timestamp}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("PAATOSKYSYMYS")
    lines.append(question)
    lines.append("")
    if v1_output:
        lines.append("=" * 60)
        lines.append("VAIHE 1 - TAUSTAKARTOITUS")
        lines.append(v1_output)
        lines.append("")
    if v1_reflection:
        lines.append("OMA REFLEKTIO")
        lines.append(v1_reflection)
        lines.append("")
    if v2_alternatives:
        lines.append("=" * 60)
        lines.append("VAIHE 2 - VAHVISTETUT VAIHTOEHDOT")
        lines.append(v2_alternatives)
        lines.append("")
    if v3_output:
        lines.append("=" * 60)
        lines.append("VAIHE 3 - VERTAILUTAULUKKO")
        lines.append(v3_output)
        lines.append("")
    if final_decision:
        lines.append("=" * 60)
        lines.append("VAIHE 4 - OMA VALINTA")
        lines.append(final_decision)
        lines.append("")
    if v4_output:
        lines.append("AI:N KRIITTINEN TARKASTELU")
        lines.append(v4_output)
        lines.append("")
    return "\n".join(lines)

def build_html_export(question, v1_output, v1_reflection, v2_alternatives, v3_output, final_decision, v4_output):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    def md_to_html(text):
        if not text:
            return ""
        import re
        # Tables
        lines = text.split("\n")
        result = []
        in_table = False
        for line in lines:
            if "|" in line and line.strip().startswith("|"):
                if not in_table:
                    result.append("<table border='1' cellpadding='6' cellspacing='0' style='border-collapse:collapse;width:100%;margin:12px 0;'>")
                    in_table = True
                if re.match(r"^\|[\s\-|]+\|$", line.strip()):
                    continue
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                result.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
            else:
                if in_table:
                    result.append("</table>")
                    in_table = False
                line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
                line = re.sub(r"^### (.+)$", r"<h3>\1</h3>", line)
                line = re.sub(r"^## (.+)$", r"<h2>\1</h2>", line)
                line = re.sub(r"^# (.+)$", r"<h1>\1</h1>", line)
                line = re.sub(r"^- (.+)$", r"<li>\1</li>", line)
                result.append(line if line.strip() else "<br>")
        if in_table:
            result.append("</table>")
        return "\n".join(result)

    sections = []
    if v1_output:
        sections.append(f"<h2>Vaihe 1 - Taustakartoitus</h2>{md_to_html(v1_output)}")
    if v1_reflection:
        sections.append(f"<h2>Oma reflektio</h2><p>{v1_reflection}</p>")
    if v2_alternatives:
        sections.append(f"<h2>Vaihe 2 - Vahvistetut vaihtoehdot</h2><pre>{v2_alternatives}</pre>")
    if v3_output:
        sections.append(f"<h2>Vaihe 3 - Vertailutaulukko</h2>{md_to_html(v3_output)}")
    if final_decision:
        sections.append(f"<h2>Oma valinta</h2><p>{final_decision}</p>")
    if v4_output:
        sections.append(f"<h2>Vaihe 4 - Kriittinen tarkastelu</h2>{md_to_html(v4_output)}")

    html = f"""<!DOCTYPE html>
<html lang="fi">
<head>
<meta charset="UTF-8">
<title>Paatostuki - {timestamp}</title>
<style>
  body {{ font-family: Georgia, serif; max-width: 900px; margin: 40px auto; padding: 0 20px; color: #222; }}
  h1 {{ font-size: 1.6em; border-bottom: 2px solid #333; padding-bottom: 8px; }}
  h2 {{ font-size: 1.2em; margin-top: 32px; color: #444; border-left: 4px solid #888; padding-left: 10px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
  td {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; font-size: 0.9em; }}
  pre {{ background: #f5f5f5; padding: 12px; white-space: pre-wrap; }}
  .meta {{ color: #888; font-size: 0.9em; }}
  @media print {{ body {{ margin: 20px; }} }}
</style>
</head>
<body>
<h1>Strateginen paatostuki - Sessioraportti</h1>
<p class="meta">Luotu: {timestamp}</p>
<h2>Paatoskysymys</h2>
<p><strong>{question}</strong></p>
{"".join(sections)}
</body>
</html>"""
    return html

# --- Session state ---
for key in ["v1_output", "v1_reflection", "v2_output", "v2_alternatives", "v3_output", "v4_output", "final_decision"]:
    if key not in st.session_state:
        st.session_state[key] = None

# --- UI ---
st.title("Strateginen paatostuki")

# VAIHE 1
st.header("Vaihe 1 - Tiedon hankinta")
st.caption("AI laajentaa kysymyksesi tietotarpeiksi, oletuksiksi ja vaihtoehtoisiksi kehyksiksi. Se ei suosittele ratkaisua.")

question = st.text_area("Paatoskysymys", placeholder="esim. Pitaisiko avata toinen toimipiste Tampereelle?", height=100)

if st.button("Analysoi"):
    if not question.strip():
        st.warning("Kirjoita ensin paatoskysymys.")
    else:
        with st.spinner("AI kartoittaa tietotarpeet..."):
            try:
                result = call_claude(SYSTEM_PROMPT_V1, question)
                st.session_state.v1_output = result
                for key in ["v1_reflection", "v2_output", "v2_alternatives", "v3_output", "v4_output", "final_decision"]:
                    st.session_state[key] = None
            except Exception as e:
                st.error(f"Virhe API-kutsussa: {e}")

if st.session_state.v1_output:
    st.markdown("---")
    st.subheader("AI:n taustakartoitus")
    st.markdown(st.session_state.v1_output)
    st.markdown("---")
    st.subheader("Sinun vuorosi")

    reflection = st.text_area(
        "Oma reflektio (pakollinen ennen seuraavaan vaiheeseen siirtymista)",
        height=150,
        placeholder="Mitka tietotarpeet ovat oikeasti kriittisia? Mitka oletukset pitavat? Mika kehys sopii parhaiten kontekstiisi?"
    )

    if st.button("Siirry vaiheeseen 2", disabled=len(reflection.strip()) < 20):
        st.session_state.v1_reflection = reflection

# VAIHE 2
if st.session_state.v1_reflection:
    st.markdown("---")
    st.header("Vaihe 2 - Vaihtoehtojen muotoilu")
    st.caption("Sina muotoilet vaihtoehdot. AI tarkistaa etta ne ovat konkreettisia ja erillisia - ei arvota eika valitse.")

    alternatives_draft = st.text_area(
        "Kirjoita 2-4 vaihtoehtoa (yksi per rivi)",
        height=150,
        placeholder="Vaihtoehto A: Avataan toimipiste Tampereelle ensi vuonna\nVaihtoehto B: Kasvatetaan nykyista toimipistetta\nVaihtoehto C: Ei muutoksia talla hetkella"
    )

    if st.button("Pyyda AI:lta muotoiluapu"):
        if not alternatives_draft.strip():
            st.warning("Kirjoita ensin vaihtoehdot.")
        else:
            with st.spinner("AI tarkistaa vaihtoehtojen muotoilun..."):
                try:
                    user_msg = f"""Alkuperainen paatoskysymys: {question}

Kayttajan reflektio taustakartoituksesta: {st.session_state.v1_reflection}

Kayttajan muotoilemat vaihtoehdot:
{alternatives_draft}"""
                    result = call_claude(SYSTEM_PROMPT_V2, user_msg)
                    st.session_state.v2_output = result
                except Exception as e:
                    st.error(f"Virhe API-kutsussa: {e}")

    if st.session_state.v2_output:
        st.markdown("---")
        st.subheader("AI:n huomiot vaihtoehtojen muotoilusta")
        st.markdown(st.session_state.v2_output)
        st.markdown("---")
        st.subheader("Vahvista lopulliset vaihtoehdot")

        final_alternatives = st.text_area(
            "Lopulliset vaihtoehdot (yksi per rivi)",
            value=alternatives_draft,
            height=150
        )

        if st.button("Siirry vaiheeseen 3", disabled=len(final_alternatives.strip()) < 10):
            st.session_state.v2_alternatives = final_alternatives

# VAIHE 3
if st.session_state.v2_alternatives:
    st.markdown("---")
    st.header("Vaihe 3 - Vertailu sinun kriteereillas")
    st.caption("Sina maaritelet kriteerit. AI tayttaa vertailutaulukon - ei painota eika suosittele.")

    st.markdown("**Vaihtoehdot vertailussa:**")
    st.code(st.session_state.v2_alternatives)

    criteria = st.text_area(
        "Maaritele vertailukriteerit (yksi per rivi)",
        height=150,
        placeholder="Taloudellinen riski\nHenkiloston kuormitus\nBrandivaikutus\nToteutusaikataulu"
    )

    if st.button("Tuota vertailutaulukko"):
        if not criteria.strip():
            st.warning("Kirjoita ensin kriteerit.")
        else:
            with st.spinner("AI rakentaa vertailutaulukon..."):
                try:
                    user_msg = f"""Paatoskysymys: {question}

Vaihtoehdot:
{st.session_state.v2_alternatives}

Vertailukriteerit:
{criteria}"""
                    result = call_claude(SYSTEM_PROMPT_V3, user_msg)
                    st.session_state.v3_output = result
                except Exception as e:
                    st.error(f"Virhe API-kutsussa: {e}")

    if st.session_state.v3_output:
        st.markdown("---")
        st.subheader("Vertailutaulukko")
        st.markdown(st.session_state.v3_output, unsafe_allow_html=True)
        st.markdown("---")

        decision = st.text_area(
            "Tee valintasi ja perustele se lyhyesti",
            height=120,
            placeholder="Valitsen vaihtoehdon X koska..."
        )

        if st.button("Siirry vaiheeseen 4", disabled=len(decision.strip()) < 20):
            st.session_state.final_decision = decision

# VAIHE 4
if st.session_state.final_decision:
    st.markdown("---")
    st.header("Vaihe 4 - Valinnan kyseenalaistaminen")
    st.caption("AI ei kumoa valintaasi eika suosittele toista. Se kysyy mita et ehka ole harkinnut.")

    st.markdown(f"**Valintasi:** {st.session_state.final_decision}")

    if st.button("Kyseenalaista valinta"):
        with st.spinner("AI tarkastelee valintaasi kriittisesti..."):
            try:
                user_msg = f"""Paatoskysymys: {question}

Vaihtoehdot olivat:
{st.session_state.v2_alternatives}

Vertailutaulukko:
{st.session_state.v3_output}

Kayttajan valinta ja perustelu:
{st.session_state.final_decision}"""
                result = call_claude(SYSTEM_PROMPT_V4, user_msg)
                st.session_state.v4_output = result
            except Exception as e:
                st.error(f"Virhe API-kutsussa: {e}")

    if st.session_state.v4_output:
        st.markdown("---")
        st.subheader("AI:n kriittinen tarkastelu")
        st.markdown(st.session_state.v4_output)
        st.markdown("---")
        st.success("Prosessi valmis.")

        # --- LATAUSNAPIT ---
        st.subheader("Lataa sessioraportti")

        txt_content = build_text_export(
            question,
            st.session_state.v1_output,
            st.session_state.v1_reflection,
            st.session_state.v2_alternatives,
            st.session_state.v3_output,
            st.session_state.final_decision,
            st.session_state.v4_output
        )

        html_content = build_html_export(
            question,
            st.session_state.v1_output,
            st.session_state.v1_reflection,
            st.session_state.v2_alternatives,
            st.session_state.v3_output,
            st.session_state.final_decision,
            st.session_state.v4_output
        )

        timestamp_file = datetime.now().strftime("%Y%m%d_%H%M")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Lataa tekstitiedostona (.txt)",
                data=txt_content.encode("utf-8"),
                file_name=f"paatossessio_{timestamp_file}.txt",
                mime="text/plain"
            )
        with col2:
            st.download_button(
                label="Lataa HTML-raporttina (.html)",
                data=html_content.encode("utf-8"),
                file_name=f"paatossessio_{timestamp_file}.html",
                mime="text/html"
            )

        st.caption("HTML-tiedoston voi avata selaimessa ja tulostaa PDF:ksi (Ctrl+P).")
