import streamlit as st
import langcodes
from deep_translator import GoogleTranslator
from langdetect import DetectorFactory, LangDetectException, detect
from spellchecker import SpellChecker
from nltk.tokenize import TreebankWordDetokenizer, wordpunct_tokenize

DetectorFactory.seed = 0
MIN_INPUT_LENGTH = 3

SPELL_LANGS = {
    "en", "es", "fr", "pt", "de",
    "ru", "ar", "eu", "lv", "nl"
}

TARGET_LANGS = {
    "Vietnamese": "vi",
    "English": "en",
    "French": "fr",
    "Japanese": "ja",
    "Chinese": "zh-CN",
    "Korean": "ko",
    "Spanish": "es",
    "German": "de",
}

EXAMPLES_T = [
    "Every morning, I drink a cup of coffee.",
    "Bonjour, comment allez-vous?",
    "Xin chao, hom nay troi dep qua.",
]

EXAMPLES_S = [
    "Yesturday, I recieveed a mesage from my freind.",
    "Definately a great oppurtunity.",
    "Je voudraiis allerr au marchee.",
]

@st.cache_resource(show_spinner=False)

def get_spellchecker(lang):
    return SpellChecker(language=lang)

def language(code):
    try:
        return langcodes.Language.get(code).display_name()
    except Exception:
        return code or "Unknown"
    
def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return None
    
def fix_typos(text, code):
    spellcheck = get_spellchecker(code)
    tokens = wordpunct_tokenize(text)
    fixed = []

    for token in tokens:
        if token.isalpha() and len(token) > 1:
            suggestion = spellcheck.correction(token.lower()) or token
            suggestion = suggestion.title() if token.istitle() else suggestion
            suggestion = suggestion.upper() if token.isupper() else suggestion
            fixed.append(suggestion)
        else:
            fixed.append(token)
    print(fixed)
    return TreebankWordDetokenizer().detokenize(fixed), fixed != tokens


def run_translation(raw, target_code):
    text = raw.strip()
    if len(text) < MIN_INPUT_LENGTH:
        return {'ok' : False, 'error' : f"Input at least {MIN_INPUT_LENGTH} characters"}
    
    text_lang = detect_language(text)
    if text_lang is None:
        return {'ok' : False, 'error' : "Language not supported or could not detect language"}
    elif text_lang == target_code:
        return {
            'ok' : True,
            'orginial_language' : language(text_lang),
            'target_language' : language(target_code),
            'translated' : text,
            'note' : "Already in targetted language"
        }

    try:
        translated = GoogleTranslator(source=text_lang, target=target_code).translate(text)
    except Exception as e:
        return {'ok' : False, 'error' : f"Translation Error: {e}"}
    
    return {
        'ok' : True,
        'orginial_language' : language(text_lang),
        'target_language' : language(target_code),
        'translated' : translated,
        'note' : "Success"
    }

def run_spellcheck(raw):
    text = raw.strip()
    if len(text) < MIN_INPUT_LENGTH:
        return {'ok' : False, 'error' : f"Input at least {MIN_INPUT_LENGTH} characters"}
    
    text_lang = detect_language(text)
    if text_lang is None:
        return {'ok' : False, 'error' : "Language not supported or could not detect language"}
    
    if text_lang not in SPELL_LANGS:
        return {'ok' : False, 'error' : f"{language(text_lang)} not supported ({text_lang})"}
    
    fixed, changed = fix_typos(text, text_lang)
    
    return {
        'ok' : True,
        'language' : language(text_lang),
        'fixed' : fixed,
        'changed' : changed
    }

st.set_page_config(page_title="NLP Pipeline Demo", layout="centered")
st.title("Streamlit NLP Pipeline Demo")
st.caption("Two features: Spellchecker - Translator")

tab_t, tab_s = st.tabs(["Translation", "Spellcheck"])

with tab_t:
    st.session_state.setdefault("res_t", None)

    with st.expander("Examples"):
        for ex in EXAMPLES_T:
            st.markdown(f"- {ex}")

    with st.form("form_translate"):
        text_t = st.text_area("Sentence to be translated", height=90,
                              placeholder="Enter a sentence in any language...")
        target = st.selectbox("Translate to", list(TARGET_LANGS.keys()))
        submitted_t = st.form_submit_button("Dịch", type="primary")

    if submitted_t:
        st.session_state.res_t = run_translation(text_t, TARGET_LANGS[target])

    res = st.session_state.res_t
    if res:
        if res["ok"]:
            st.caption(f"Source: {res['orginial_language']}  →  Target: {res['target_language']}")
            st.markdown(res["translated"])
            if res.get("note"):
                st.info(res["note"])
        else:
            st.warning(res["error"])


with tab_s:
    st.session_state.setdefault("res_s", None)

    with st.expander("Examples"):
        for ex in EXAMPLES_S:
            st.markdown(f"- {ex}")
    st.caption(f"Supported languages: {', '.join(sorted(SPELL_LANGS))}")

    with st.form("form_spell"):
        text_s = st.text_area("Sentence to be checked", height=90,
                              placeholder="Enter a sentence in any language...")
        submitted_s = st.form_submit_button("Kiểm tra", type="primary")

    if submitted_s:
        st.session_state.res_s = run_spellcheck(text_s)

    res = st.session_state.res_s
    if res:
        if res["ok"]:
            st.caption(f"Language: {res['language']}")
            st.markdown(res["fixed"])
            st.caption("Spellchecked" if res["changed"] else "No typos")
        else:
            st.caption(res["error"])



