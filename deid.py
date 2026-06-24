"""De-identification / re-identification using Microsoft Presidio.

Detects PHI-style identifiers in a transcript and replaces each with a stable,
reversible placeholder (e.g. [PERSON_1], [LOCATION_1]). The mapping lives only in
memory for the duration of a single request -- nothing is written to disk.

IMPORTANT (relay to the clinician): automated de-identification of free-text
therapy transcripts is leaky. It reliably removes *structured* identifiers
(names, dates, phones) but cannot catch every *narrative* quasi-identifier
("my home country", a specific life event, a relative's job). This reduces risk;
it is not, by itself, HIPAA Safe-Harbor de-identification. Pair it with a BAA.
"""

from functools import lru_cache

# Identifiers we redact by default. PERSON / LOCATION / DATE_TIME are the ones
# that actually show up in therapy narratives; the rest are cheap insurance.
DEFAULT_ENTITIES = [
    "PERSON",
    "LOCATION",
    "DATE_TIME",
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "US_SSN",
    "CREDIT_CARD",
    "IP_ADDRESS",
    "IBAN_CODE",
    "US_DRIVER_LICENSE",
    "US_PASSPORT",
    "MEDICAL_LICENSE",
    "NRP",  # nationality / religious / political group
]


@lru_cache(maxsize=1)
def _analyzer():
    # Imported lazily so the module loads fast and errors surface with a clear
    # message if Presidio / the spaCy model aren't installed yet.
    from presidio_analyzer import AnalyzerEngine

    return AnalyzerEngine()


def deidentify(text, entities=None, threshold=0.4):
    """Return (deidentified_text, mapping).

    mapping is {placeholder: original_text}. Identical surface strings of the
    same entity type collapse to the same placeholder so the model sees a
    consistent referent (every "Michael" -> [PERSON_1]).
    """
    if not text or not text.strip():
        return text, {}

    results = _analyzer().analyze(
        text=text,
        entities=entities or DEFAULT_ENTITIES,
        language="en",
        score_threshold=threshold,
    )

    # Resolve overlaps: walk left-to-right, prefer the longest span starting
    # earliest, and skip anything that overlaps an already-chosen span.
    results = sorted(results, key=lambda r: (r.start, -(r.end - r.start)))
    chosen, last_end = [], -1
    for r in results:
        if r.start >= last_end:
            chosen.append(r)
            last_end = r.end

    mapping = {}          # placeholder -> original
    seen = {}             # (entity_type, lowered_text) -> placeholder
    counters = {}         # entity_type -> running count
    out, cursor = [], 0

    for r in sorted(chosen, key=lambda r: r.start):
        original = text[r.start:r.end]
        key = (r.entity_type, original.lower())
        ph = seen.get(key)
        if ph is None:
            counters[r.entity_type] = counters.get(r.entity_type, 0) + 1
            ph = f"[{r.entity_type}_{counters[r.entity_type]}]"
            seen[key] = ph
            mapping[ph] = original
        out.append(text[cursor:r.start])
        out.append(ph)
        cursor = r.end

    out.append(text[cursor:])
    return "".join(out), mapping


def reidentify(text, mapping):
    """Replace placeholders with their originals. Longest placeholders first so
    [PERSON_12] is restored before [PERSON_1] can match a prefix of it."""
    for ph in sorted(mapping, key=len, reverse=True):
        text = text.replace(ph, mapping[ph])
    return text
