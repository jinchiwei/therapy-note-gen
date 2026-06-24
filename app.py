"""Local-only web UI for generating de-identified therapy notes.

Run:  python app.py
Then open http://127.0.0.1:5005 in a browser.

Privacy posture:
- Binds to 127.0.0.1 only (not reachable from the network).
- Transcript and the de-id mapping live in memory for one request, then are
  discarded. Nothing is written to disk. No logging of transcript content.
"""

import os

from dotenv import load_dotenv

load_dotenv()  # read ANTHROPIC_API_KEY (and NOTE_MODEL / PORT) from .env automatically

from flask import Flask, render_template_string, request, jsonify

from deid import deidentify, reidentify
from notegen import generate_note, DEFAULT_MODEL

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Therapy Note Generator</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --turquoise:#40E0D0; --deeppink:#FF1493; --amber:#F0C840; --blueviolet:#8A2BE2;
    --ink:#16181d; --paper:#faf9f7; --line:#e7e4df; --muted:#6b6f76;
    --sans:"Geist", -apple-system, "Segoe UI", Roboto, sans-serif;
    --mono:"Geist Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  }
  * { box-sizing: border-box; }
  body { font: 15px/1.5 var(--sans); color: var(--ink); margin: 0; background: var(--paper); }
  header.bar { background: var(--ink); color: #fff; padding: 22px 20px 20px; }
  header.bar .inner { max-width: 900px; margin: 0 auto; }
  header.bar h1 { font: 600 21px/1.2 var(--mono); color: var(--turquoise);
                  margin: 0; letter-spacing: -.01em; }
  header.bar .sub { color: #b9bdc6; margin: 6px 0 0; font: 13px/1.5 var(--mono); }
  .rule { height: 3px; background: linear-gradient(90deg, var(--turquoise), var(--deeppink)); }
  .wrap { max-width: 900px; margin: 0 auto; padding: 26px 20px 64px; }
  label { font: 600 13px/1.4 var(--mono); display: block; margin: 0 0 6px;
          letter-spacing: .01em; color: var(--ink); }
  textarea { width: 100%; min-height: 240px; padding: 12px; border: 1px solid var(--line);
             border-radius: 10px; font: 13px/1.5 var(--mono); resize: vertical; background: #fff; }
  textarea:focus, select:focus { outline: 2px solid var(--turquoise); outline-offset: 1px; }
  .row { display: flex; gap: 14px; align-items: center; margin: 14px 0; flex-wrap: wrap; }
  select, button { font: inherit; }
  select { padding: 9px 12px; border: 1px solid var(--line); border-radius: 10px;
           background: #fff; font: 13px/1.4 var(--mono); }
  button { background: var(--turquoise); color: var(--ink); border: 0; padding: 10px 20px;
           border-radius: 10px; font: 600 14px var(--mono); cursor: pointer; }
  button:hover { filter: brightness(.95); }
  button:disabled { opacity: .5; cursor: default; }
  .ghost { background: #fff; color: var(--ink); border: 1px solid var(--line); }
  .ghost.copied { background: var(--deeppink); color: #fff; border-color: var(--deeppink); }
  .out { margin-top: 24px; display: none; }
  pre { white-space: pre-wrap; background: #fff; border: 1px solid var(--line);
        border-left: 3px solid var(--turquoise); border-radius: 10px; padding: 16px;
        font: 13px/1.6 var(--mono); }
  details { margin-top: 16px; }
  summary { cursor: pointer; color: var(--muted); font: 13px var(--mono); }
  .chip { display:inline-block; background:rgba(64,224,208,.16); color:#0f7a70;
          border-radius:6px; padding:2px 8px; margin:2px; font: 12px/1.6 var(--mono); }
  .err { color: var(--deeppink); margin-top: 12px; font-weight: 500; }
  .note { color: var(--muted); font-size: 12px; margin-top: 10px; }
</style>
</head>
<body>
<header class="bar">
  <div class="inner">
    <h1>Therapy Note Generator</h1>
    <p class="sub">local &middot; de-identifies before anything leaves this machine &middot; model: {{ model }}</p>
  </div>
</header>
<div class="rule"></div>
<div class="wrap">

  <label for="t">Session transcript</label>
  <textarea id="t" placeholder="Paste the session transcript here..."></textarea>

  <div class="row">
    <select id="model">
      <option value="">Default ({{ model }})</option>
      <option value="claude-opus-4-8">claude-opus-4-8 (highest quality)</option>
      <option value="claude-sonnet-4-6">claude-sonnet-4-6 (cheaper)</option>
    </select>
    <button id="go">Generate note</button>
    <span id="status" class="note"></span>
  </div>

  <div id="out" class="out">
    <div class="row" style="justify-content: space-between;">
      <label style="margin:0;">Generated note</label>
      <button class="ghost" id="copy">Copy</button>
    </div>
    <pre id="note"></pre>

    <details>
      <summary>What was redacted before sending (audit)</summary>
      <div id="redactions" style="margin-top:10px;"></div>
      <p class="note">These spans were replaced with placeholders before the transcript
        was sent to the model. Review to confirm nothing identifying slipped through.</p>
    </details>
  </div>

  <p id="err" class="err"></p>
</div>

<script>
const $ = s => document.querySelector(s);
$("#go").addEventListener("click", async () => {
  const transcript = $("#t").value.trim();
  $("#err").textContent = "";
  if (!transcript) { $("#err").textContent = "Paste a transcript first."; return; }
  $("#go").disabled = true; $("#status").textContent = "De-identifying and generating...";
  try {
    const r = await fetch("/generate", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ transcript, model: $("#model").value })
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || "Request failed");
    $("#note").textContent = data.note;
    const red = $("#redactions"); red.innerHTML = "";
    const entries = Object.entries(data.mapping);
    if (entries.length === 0) red.innerHTML = "<span class='note'>No identifiers detected.</span>";
    else entries.forEach(([ph, orig]) =>
      red.insertAdjacentHTML("beforeend", `<span class="chip">${ph} = ${orig}</span>`));
    $("#out").style.display = "block";
    $("#status").textContent = "";
  } catch (e) {
    $("#err").textContent = e.message;
    $("#status").textContent = "";
  } finally { $("#go").disabled = false; }
});
$("#copy").addEventListener("click", () => {
  navigator.clipboard.writeText($("#note").textContent);
  const b = $("#copy"); b.textContent = "Copied"; b.classList.add("copied");
  setTimeout(() => { b.textContent = "Copy"; b.classList.remove("copied"); }, 1200);
});
</script>
</body>
</html>"""


@app.get("/")
def index():
    return render_template_string(PAGE, model=DEFAULT_MODEL)


@app.post("/generate")
def generate():
    data = request.get_json(force=True)
    transcript = (data.get("transcript") or "").strip()
    model = (data.get("model") or "").strip() or None
    if not transcript:
        return jsonify(error="Empty transcript."), 400

    deid_text, mapping = deidentify(transcript)
    try:
        note = generate_note(deid_text, model=model)
    except Exception as e:  # surface API/key errors to the UI instead of a 500 page
        return jsonify(error=f"Generation failed: {e}"), 502

    note = reidentify(note, mapping)  # usually a no-op; notes are name-free by style
    return jsonify(note=note, mapping=mapping)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5005"))
    app.run(host="127.0.0.1", port=port, debug=False)
