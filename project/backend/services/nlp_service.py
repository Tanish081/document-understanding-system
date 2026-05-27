"""NLP service — Named Entity Recognition and extractive summarization via spaCy.

Uses en_core_web_md (preferred) with en_core_web_sm as a fallback.
No transformers, no external API calls, no extra downloads beyond spaCy.

Accuracy strategy:
  - Text is cleaned of PDF noise before NLP (page numbers, headers, hyphenation).
  - Entities are validated using POS tags: PERSON / GPE / LOC must contain at
    least one PROPN token.  This catches common misclassifications like sport
    names, common nouns, and salutations.
  - Bullet / dash artefacts are stripped from entity surfaces.
  - Summarizer combines TF frequency scoring with a position bonus.
"""

import re
from collections import Counter

import spacy

try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    nlp = spacy.load("en_core_web_sm")

_WANTED_LABELS = {"PERSON", "ORG", "DATE", "GPE", "LOC", "MONEY", "TIME", "PERCENT"}
_MAX_CHARS = 950_000

# Common words that spaCy frequently misclassifies as PERSON.
_PERSON_BLOCKLIST = {
    "gold", "silver", "bronze", "medal", "girls", "boys", "men", "women",
    "madam", "sir", "miss", "master", "subject", "class", "year",
    "college", "university", "school", "institute", "department",
    "committee", "board", "hindi", "english", "marathi", "language",
    "sports", "games", "krida",
}

# Language names that spaCy often misclassifies as GPE (geopolitical entity).
_LANGUAGE_NAMES = {
    "hindi", "english", "marathi", "punjabi", "urdu", "tamil", "telugu",
    "bengali", "gujarati", "kannada", "malayalam", "odia", "sanskrit",
    "french", "german", "spanish", "chinese", "arabic", "japanese",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clean_for_nlp(text):
    """Strip PDF artefacts (page numbers, headers, broken hyphenation) before NLP."""
    lines = text.split("\n")
    kept = []
    for line in lines:
        line = line.strip()
        if not line or len(line) < 4:
            continue
        alpha_ratio = sum(c.isalpha() for c in line) / len(line)
        if alpha_ratio < 0.45 and len(line) < 35:
            continue
        # All-uppercase short lines are section headers.
        if line.isupper() and len(line.split()) <= 6:
            continue
        # Letter/form header lines and salutations carry no summarisable content.
        if re.match(r"^(subject|to|from|date|ref|re|cc)\s*[:,]", line.lower()):
            continue
        if re.match(r"^dear\b", line.lower()):
            continue
        kept.append(line)

    joined = " ".join(kept)
    joined = re.sub(r"-\s+([a-z])", r"\1", joined)   # fix hyphenated line-breaks
    joined = re.sub(r"\s+", " ", joined).strip()
    return joined


def _clean_surface(text):
    """Remove leading/trailing bullets, dashes, and punctuation from entity text."""
    text = re.sub(r"^[•\-–—·\s]+", "", text)
    text = re.sub(r"[•\-–—·\s]+$", "", text)
    return text.strip()


def _has_propn(ent):
    """Return True if the entity contains at least one proper noun token."""
    return any(t.pos_ == "PROPN" for t in ent)


def _is_valid(ent, surface, label):
    """Return True if this entity passes label-specific validation rules."""
    words = surface.lower().split()
    word_count = len(words)

    if label == "PERSON":
        if word_count > 5:
            return False
        if any(w in _PERSON_BLOCKLIST for w in words):
            return False
        # Require at least one proper noun — filters salutations, common nouns, etc.
        if not _has_propn(ent):
            return False

    elif label in ("GPE", "LOC"):
        # Common nouns and sport names are not proper locations.
        if not _has_propn(ent):
            return False
        # Language names are frequently misclassified as GPE.
        if surface.lower() in _LANGUAGE_NAMES:
            return False

    elif label == "ORG":
        # Form labels like "Subject: Application For" start with a field name + colon.
        if re.match(r"^\w[\w\s]{0,15}:\s", surface):
            return False
        if word_count > 12:
            return False
        # Require at least one PROPN — filters "Physical Education" etc.
        if not _has_propn(ent):
            return False
        # Language names are not organizations.
        if surface.lower() in _LANGUAGE_NAMES:
            return False

    return True


# ── Named Entity Recognition ──────────────────────────────────────────────────

def extract_entities(text):
    """Run NER and return a validated, deduplicated entity list.

    Each item: { "text": str, "label": str }
    """
    if not text or not text.strip():
        return []

    cleaned = _clean_for_nlp(text)
    doc = nlp(cleaned[:_MAX_CHARS])

    seen: set = set()
    entities = []
    for ent in doc.ents:
        if ent.label_ not in _WANTED_LABELS:
            continue

        surface = _clean_surface(ent.text)
        if len(surface) < 2 or surface.isdigit() or len(surface) > 80:
            continue
        if not _is_valid(ent, surface, ent.label_):
            continue

        key = (surface.lower(), ent.label_)
        if key in seen:
            continue
        seen.add(key)
        entities.append({"text": surface, "label": ent.label_})

    return entities


# ── Extractive summarization ──────────────────────────────────────────────────

def extract_summary(text, num_sentences=5):
    """Return the top-N most informative sentences using TF + position scoring."""
    if not text or not text.strip():
        return ""

    cleaned = _clean_for_nlp(text)
    doc = nlp(cleaned[:_MAX_CHARS])

    sentences = []
    for sent in doc.sents:
        surface = sent.text.strip()
        if len(surface) < 40:
            continue
        if sum(1 for t in sent if t.is_alpha) < 7:
            continue
        sentences.append(sent)

    if not sentences:
        return cleaned[:500]
    if len(sentences) <= num_sentences:
        return " ".join(s.text.strip() for s in sentences)

    freq: Counter = Counter()
    for token in doc:
        if token.is_alpha and not token.is_stop:
            freq[token.lemma_.lower()] += 1

    if freq:
        max_freq = max(freq.values())
        for w in freq:
            freq[w] /= max_freq

    total = len(sentences)
    scored: dict = {}
    cutoff = max(1, int(total * 0.25))

    for idx, sent in enumerate(sentences):
        content = [
            freq[t.lemma_.lower()]
            for t in sent
            if t.is_alpha and not t.is_stop and t.lemma_.lower() in freq
        ]
        if not content:
            continue
        tf_score = sum(content) / len(content)
        position_bonus = max(0.0, 0.3 * (1.0 - idx / cutoff)) if idx < cutoff else 0.0
        scored[sent] = tf_score + position_bonus

    top = sorted(scored, key=scored.get, reverse=True)[:num_sentences]
    top_ordered = sorted(top, key=lambda s: s.start)
    return " ".join(s.text.strip() for s in top_ordered)
