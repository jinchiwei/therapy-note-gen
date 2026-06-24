"""Few-shot anchors: SYNTHETIC notes in the clinician's house style.

These are entirely fictional — invented client, invented content — and exist only
to demonstrate the exact section structure, checkbox conventions, voice, and level
of abstraction the model should reproduce. No real patient material is in this file,
so it is safe to commit to a public repo.

To use real de-identified notes locally for higher fidelity, create an
`examples_local.py` (gitignored) that defines `EXEMPLARS`; notegen.py prefers it.
NEVER commit real patient material, even de-identified.
"""

EXEMPLARS = [
    # --- Synthetic continuing session #1 ---
    """Observations:
Client presents on time for in person therapy appointment. He presents with "okay" mood, full affect. He discussed ongoing stress related to a recent job change and the adjustment to a new team, noting difficulty knowing whether he is meeting expectations. He reflected on a longstanding tendency toward perfectionism and a habit of measuring his worth through productivity, observing that quieter periods often leave him feeling restless and self critical.

Client further explored his relationship with rest, describing guilt when taking time for himself and a belief that he must continually prove his value to others. He reflected on how this pattern may have developed and discussed wanting to build a steadier sense of self that does not depend entirely on external achievement.

Interventions:
Explored clients stress regarding his recent job change and adjustment to a new team, as well as his perfectionism and the relationship between productivity and self worth.

X Support
X Affect Naming
X CBT Techniques
X Exploration

Response to Interventions:
Client listened and engaged actively in session.

X Listened X Concurred X New information
X Verbalized insight X Affect more available

Plan:
Continue weekly therapy.""",

    # --- Synthetic continuing session #2 (no Affect Naming, to show variation) ---
    """Observations:
Client presents on time for in person therapy appointment. He presents with "good" mood, full affect. He discussed a recent visit with family and reflected on shifting dynamics in those relationships as he has grown older. He described feeling more able to set small boundaries than in the past, though noted lingering discomfort when others express disappointment.

Client reflected on his tendency to take responsibility for managing other people's emotions and explored where this pattern may have originated. He expressed a wish to remain caring while allowing others to hold their own feelings, and noted some recent progress in tolerating discomfort without immediately attempting to resolve it.

Interventions:
Explored clients reflections on changing family dynamics and boundary setting, as well as his tendency to feel responsible for others' emotions.

X Support
X CBT Techniques
X Exploration

Response to Interventions:
Client listened and engaged actively in session.

X Listened X Concurred X New information
X Verbalized insight X Affect more available

Plan:
Continue weekly therapy.""",
]
