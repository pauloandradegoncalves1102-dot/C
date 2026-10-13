"""
GrammarFix — Corretor Gramatical Profissional
Arquivo único: backend (Flask) + frontend (HTML/CSS/JS embutidos)
"""

from flask import Flask, request, render_template_string
import language_tool_python
import json

app = Flask(__name__)

# ─── Template HTML ────────────────────────────────────────────────────────────

TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GrammarFix — Corretor Gramatical</title>
<style>
  :root {
    --bg: #0f1117;
    --surface: #1a1d2e;
    --surface2: #242842;
    --border: #2e3350;
    --text: #e2e4f0;
    --text-dim: #8b8fa3;
    --accent: #6c63ff;
    --accent-hover: #5a52d5;
    --error: #ff6b6b;
    --success: #51cf66;
    --warning: #ffd43b;
    --radius: 12px;
    --shadow: 0 8px 32px rgba(0,0,0,.35);
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* ── Header ── */
  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 16px 32px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  header .logo {
    width: 36px; height: 36px;
    background: var(--accent);
    border-radius: 8px;
    display: grid; place-items: center;
    font-weight: 700; font-size: 18px; color: #fff;
  }
  header h1 { font-size: 1.25rem; font-weight: 600; }
  header span { color: var(--text-dim); font-size: .85rem; margin-left: auto; }

  /* ── Main ── */
  main {
    flex: 1;
    max-width: 1100px;
    width: 100%;
    margin: 0 auto;
    padding: 32px 24px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }
  @media (max-width: 768px) { main { grid-template-columns: 1fr; } }

  .panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .panel-header {
    padding: 14px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 600;
    font-size: .9rem;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: .5px;
  }
  .panel-body {
    flex: 1;
    padding: 20px;
  }
  textarea {
    width: 100%;
    min-height: 320px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-size: 1rem;
    line-height: 1.7;
    padding: 16px;
    resize: vertical;
    outline: none;
    transition: border-color .2s;
  }
  textarea:focus { border-color: var(--accent); }
  textarea::placeholder { color: var(--text-dim); }

  .output {
    min-height: 320px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    line-height: 1.7;
    font-size: 1rem;
    overflow-y: auto;
    max-height: 500px;
    white-space: pre-wrap;
  }
  .output .err {
    background: rgba(255,107,107,.15);
    border-bottom: 2px solid var(--error);
    border-radius: 3px;
    padding: 1px 3px;
    cursor: pointer;
    transition: background .15s;
  }
  .output .err:hover { background: rgba(255,107,107,.3); }
  .output .fix {
    background: rgba(81,207,102,.12);
    border-bottom: 2px solid var(--success);
    border-radius: 3px;
    padding: 1px 3px;
  }

  /* ── Toolbar ── */
  .toolbar {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-top: 16px;
    flex-wrap: wrap;
  }
  .btn {
    padding: 10px 24px;
    border: none;
    border-radius: 8px;
    font-size: .95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all .2s;
  }
  .btn-primary {
    background: var(--accent);
    color: #fff;
  }
  .btn-primary:hover { background: var(--accent-hover); transform: translateY(-1px); }
  .btn-primary:disabled { opacity: .5; cursor: not-allowed; transform: none; }
  .btn-secondary {
    background: var(--surface2);
    color: var(--text);
    border: 1px solid var(--border);
  }
  .btn-secondary:hover { background: var(--border); }

  select {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 9px 14px;
    border-radius: 8px;
    font-size: .9rem;
    outline: none;
    cursor: pointer;
  }

  /* ── Stats bar ── */
  .stats {
    display: flex;
    gap: 20px;
    padding: 12px 20px;
    border-top: 1px solid var(--border);
    font-size: .82rem;
    color: var(--text-dim);
  }
  .stats .dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 6px;
  }
  .dot-red { background: var(--error); }
  .dot-green { background: var(--success); }

  /* ── Loading ── */
  .spinner {
    display: inline-block;
    width: 16px; height: 16px;
    border: 2px solid rgba(255,255,255,.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin .6s linear infinite;
    vertical-align: middle;
    margin-right: 8px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── Tooltip ── */
  .tooltip {
    position: absolute;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: .82rem;
    box-shadow: var(--shadow);
    z-index: 100;
    max-width: 280px;
    pointer-events: none;
  }
  .tooltip .msg { color: var(--error); font-weight: 600; margin-bottom: 4px; }
  .tooltip .sug { color: var(--success); }

  footer {
    text-align: center;
    padding: 16px;
    font-size: .78rem;
    color: var(--text-dim);
    border-top: 1px solid var(--border);
  }
</style>
</head>
<body>

<header>
  <div class="logo">G</div>
  <h1>GrammarFix</h1>
  <span>Corretor Gramatical Profissional</span>
</header>

<main>
  <!-- Input -->
  <div class="panel">
    <div class="panel-header">
      <span>Texto Original</span>
      <span id="charCount">0 caracteres</span>
    </div>
    <div class="panel-body">
      <textarea id="inputText" placeholder="Cole ou digite seu texto aqui para correção gramatical..."></textarea>
      <div class="toolbar">
        <button class="btn btn-primary" id="btnCheck" onclick="checkGrammar()">
          <span id="btnLabel">Corrigir</span>
        </button>
        <button class="btn btn-secondary" onclick="clearAll()">Limpar</button>
        <select id="langSelect">
          <option value="en-US">English (US)</option>
          <option value="en-GB">English (UK)</option>
          <option value="pt-BR">Português (BR)</option>
          <option value="fr-FR">Français</option>
          <option value="de-DE">Deutsch</option>
          <option value="es-ES">Español</option>
        </select>
      </div>
    </div>
  </div>

  <!-- Output -->
  <div class="panel">
    <div class="panel-header">
      <span>Resultado</span>
      <span id="statusBadge"></span>
    </div>
    <div class="panel-body">
      <div class="output" id="output">O texto corrigido aparecerá aqui...</div>
    </div>
    <div class="stats" id="statsBar" style="display:none;">
      <span><span class="dot dot-red"></span><span id="errCount">0</span> erros</span>
      <span><span class="dot dot-green"></span><span id="fixCount">0</span> correções</span>
      <span id="timeTaken"></span>
    </div>
  </div>
</main>

<footer>GrammarFix &copy; 2025 — Powered by LanguageTool</footer>

<script>
const inputEl = document.getElementById('inputText');
const outputEl = document.getElementById('output');
const btn = document.getElementById('btnCheck');
const btnLabel = document.getElementById('btnLabel');
const charCount = document.getElementById('charCount');
const statsBar = document.getElementById('statsBar');
const statusBadge = document.getElementById('statusBadge');

inputEl.addEventListener('input', () => {
  charCount.textContent = inputEl.value.length + ' caracteres';
});

async function checkGrammar() {
  const text = inputEl.value.trim();
  if (!text) return alert('Digite um texto para corrigir.');

  btn.disabled = true;
  btnLabel.innerHTML = '<span class="spinner"></span>Analisando...';
  statusBadge.textContent = '';
  statsBar.style.display = 'none';

  try {
    const res = await fetch('/api/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        text,
        language: document.getElementById('langSelect').value
      })
    });
    const data = await res.json();

    if (data.error) {
      outputEl.textContent = 'Erro: ' + data.error;
      return;
    }

    // Render output with highlights
    outputEl.innerHTML = '';
    let lastEnd = 0;
    let errCount = 0;

    for (const m of data.matches) {
      const start = m.offset;
      const end = start + m.errorLength;
      if (start > lastEnd) {
        outputEl.appendChild(document.createTextNode(data.corrected.slice(lastEnd, start)));
      }
      const span = document.createElement('span');
      span.className = 'err';
      span.textContent = data.corrected.slice(start, end);
      span.title = m.message;
      span.onclick = (e) => showTooltip(e, m);
      outputEl.appendChild(span);
      lastEnd = end;
      errCount++;
    }
    if (lastEnd < data.corrected.length) {
      outputEl.appendChild(document.createTextNode(data.corrected.slice(lastEnd)));
    }

    // Stats
    document.getElementById('errCount').textContent = errCount;
    document.getElementById('fixCount').textContent = errCount;
    document.getElementById('timeTaken').textContent = data.time + 's';
    statsBar.style.display = 'flex';
    statusBadge.innerHTML = errCount === 0
      ? '<span style="color:var(--success)">✓ Sem erros</span>'
      : `<span style="color:var(--warning)">${errCount} correções</span>`;

  } catch (e) {
    outputEl.textContent = 'Erro de conexão: ' + e.message;
  } finally {
    btn.disabled = false;
    btnLabel.textContent = 'Corrigir';
  }
}

function showTooltip(e, m) {
  document.querySelectorAll('.tooltip').forEach(t => t.remove());
  const tip = document.createElement('div');
  tip.className = 'tooltip';
  tip.innerHTML = `<div class="msg">${m.message}</div>` +
    (m.replacements.length ? `<div class="sug">Sugestão: ${m.replacements[0]}</div>` : '');
  document.body.appendChild(tip);
  tip.style.left = e.pageX + 'px';
  tip.style.top = (e.pageY + 12) + 'px';
  setTimeout(() => tip.remove(), 3000);
}

function clearAll() {
  inputEl.value = '';
  outputEl.textContent = 'O texto corrigido aparecerá aqui...';
  charCount.textContent = '0 caracteres';
  statsBar.style.display = 'none';
  statusBadge.textContent = '';
}
</script>
</body>
</html>
"""

# ─── Rotas ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(TEMPLATE)


@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.get_json(force=True)
    text = data.get("text", "")
    lang = data.get("language", "en-US")

    if not text.strip():
        return {"error": "Texto vazio."}

    try:
        import time
        t0 = time.time()

        tool = language_tool_python.LanguageTool(lang)
        matches = tool.check(text)
        corrected = tool.correct(text)
        elapsed = round(time.time() - t0, 2)

        # Serializar matches para o frontend
        serialized = []
        for m in matches:
            serialized.append({
                "offset": m.offset,
                "errorLength": m.error_length,   # ← snake_case
                "message": m.message,
                "replacements": m.replacements,
                "rule": m.rule_id,              # ← snake_case
    })

        return {
            "corrected": corrected,
            "matches": serialized,
            "time": elapsed,
        }

    except Exception as e:
        return {"error": str(e)}


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  ┌─────────────────────────────────────────┐")
    print("  │  GrammarFix — Corretor Gramatical     │")
    print("  │  http://localhost:5000                │")
    print("  └─────────────────────────────────────────┘\n")
    app.run(host="0.0.0.0", port=5000, debug=True)   