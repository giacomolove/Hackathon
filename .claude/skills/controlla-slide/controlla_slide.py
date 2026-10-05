"""Controllo visivo delle slide di VoceAmica (presentation/index.html).

Apre la presentazione in Chrome (o Edge) headless a più risoluzioni, attiva una slide
alla volta e misura cosa vede davvero il pubblico:

  - testo tagliato fuori dallo schermo (il body ha overflow: hidden, quindi è perso)
  - testo sovrapposto ad altro testo, incluso il piè di pagina fisso
  - contrasto WCAG fra testo e sfondo
  - carattere troppo piccolo per un proiettore
  - sfondo scuro (il team ha chiesto slide con sfondo chiaro)
  - densità di parole e tempo di parola dichiarato con data-secondi

Uso:
  python .claude/skills/controlla-slide/controlla_slide.py [presentation/index.html]
         [--risoluzioni 1280x720,1366x768,1920x1080] [--screenshot] [--budget 180]

Esce con codice 1 se trova almeno un ERRORE. Nessuna dipendenza oltre a Python 3.
"""

import argparse
import concurrent.futures
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

BROWSER_CANDIDATI = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]

# Misure eseguite dentro la pagina. Scrive il referto in <script id="__controllo">.
SONDA_JS = r"""
(function () {
  function lum(c) {
    function ch(v) { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2]);
  }
  function ratio(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  function parse(s) {
    var m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat);
    return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1];
  }
  function sopra(top, base) {
    var a = top[3];
    return [top[0] * a + base[0] * (1 - a), top[1] * a + base[1] * (1 - a), top[2] * a + base[2] * (1 - a), 1];
  }
  function coloriGradiente(s) {
    var out = [], re = /rgba?\([^)]+\)/g, m;
    while ((m = re.exec(s))) out.push(parse(m[0]));
    return out;
  }
  // Sfondo effettivo dietro un elemento: compone i background-color degli antenati.
  // Se un antenato ha un gradiente, usa il colore peggiore fra i suoi stop.
  function sfondi(el, saltaImmagine) {
    var catena = [], e = el;
    while (e && e.nodeType === 1) { catena.push(e); e = e.parentElement; }
    var basi = [[255, 255, 255, 1]];
    for (var i = catena.length - 1; i >= 0; i--) {
      var cs = getComputedStyle(catena[i]);
      var img = cs.backgroundImage;
      if (img && img !== "none" && !(saltaImmagine && catena[i] === el)) {
        var stop = coloriGradiente(img);
        if (stop.length) {
          basi = stop.reduce(function (acc, s) {
            return acc.concat(basi.map(function (b) { return sopra(s, b); }));
          }, []);
          continue;
        }
      }
      var bg = parse(cs.backgroundColor);
      if (bg && bg[3] > 0) basi = basi.map(function (b) { return sopra(bg, b); });
    }
    return basi;
  }
  function opacita(el) {
    var o = 1;
    for (var e = el; e && e.nodeType === 1; e = e.parentElement) o *= parseFloat(getComputedStyle(e).opacity);
    return o;
  }

  function rettangoliTesto(root, etichetta) {
    var out = [], tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null), n, idx = 0;
    while ((n = tw.nextNode())) {
      if (!n.nodeValue.trim()) continue;
      var el = n.parentElement, cs = getComputedStyle(el);
      if (cs.visibility === "hidden" || el.closest("script,style")) continue;
      var r = document.createRange(); r.selectNodeContents(n);
      var rs = r.getClientRects(), id = etichetta + ":" + (idx++), fs = parseFloat(cs.fontSize);
      for (var k = 0; k < rs.length; k++) {
        var q = rs[k]; if (q.width < 1 || q.height < 1) continue;
        // Il rettangolo del Range è l'area tipografica (ascendente + discendente del font),
        // più alta delle lettere vere: due righe di un titolo con interlinea stretta si
        // "toccherebbero" senza che nessun glifo si scontri. Per le sovrapposizioni si usa
        // l'ingombro dell'inchiostro: 1.15em sopra il fondo, accenti delle maiuscole inclusi.
        out.push({ id: id, el: el, l: q.left, t: q.top, r: q.right, b: q.bottom,
                   ti: q.top + Math.max(0, q.height - 1.15 * fs),
                   testo: n.nodeValue.trim().replace(/\s+/g, " ").slice(0, 60) });
      }
    }
    return out;
  }

  function misuraSlide(slide, i, piede, W, H) {
    var rep = { n: i + 1, titolo: "", errori: [], avvisi: [], parole: 0, secondi: null, sfondo: null };
    var h = slide.querySelector("h1,h2"); rep.titolo = h ? h.textContent.replace(/\s+/g, " ").trim() : "(senza titolo)";
    rep.parole = (slide.innerText.match(/[\p{L}\p{N}][\p{L}\p{N}'’,.%-]*/gu) || []).length;
    var sec = slide.getAttribute("data-secondi"); rep.secondi = sec === null ? null : parseFloat(sec);
    rep.demo = slide.hasAttribute("data-demo");

    var bgSlide = sfondi(slide, false);
    var Lmin = Math.min.apply(null, bgSlide.map(lum));
    rep.sfondo = Lmin < 0.18 ? "scuro" : "chiaro";
    if (Lmin < 0.03) rep.avvisi.push("Sfondo quasi nero: il team ha chiesto slide con sfondo non nero.");

    var testi = rettangoliTesto(slide, "s");
    var piedi = piede ? rettangoliTesto(piede, "piede") : [];

    // 1. Testo fuori dallo schermo
    var tagliati = {};
    testi.concat(piedi).forEach(function (t) {
      if (t.t < -1 || t.b > H + 1 || t.l < -1 || t.r > W + 1) tagliati[t.id] = t;
    });
    Object.keys(tagliati).forEach(function (k) {
      var t = tagliati[k];
      rep.errori.push("Testo tagliato fuori schermo (" + Math.round(t.t) + "→" + Math.round(t.b) + "px su " + H + "): «" + t.testo + "»");
    });
    if (slide.scrollHeight > slide.clientHeight + 2)
      rep.errori.push("Il contenuto è più alto della slide di " + (slide.scrollHeight - slide.clientHeight) + "px.");

    // 2. Sovrapposizioni fra testi diversi (tolleranza 2px per i bordi che si toccano)
    var tutti = testi.concat(piedi), visti = {};
    for (var a = 0; a < tutti.length; a++) {
      for (var b = a + 1; b < tutti.length; b++) {
        var p = tutti[a], q = tutti[b];
        if (p.id === q.id) continue;
        var ix = Math.min(p.r, q.r) - Math.max(p.l, q.l), iy = Math.min(p.b, q.b) - Math.max(p.ti, q.ti);
        if (ix > 2 && iy > 2) {
          var chiave = p.id + "|" + q.id; if (visti[chiave]) continue; visti[chiave] = 1;
          rep.errori.push("Testo sovrapposto: «" + p.testo + "» con «" + q.testo + "»");
        }
      }
    }

    // 3. Contrasto e 4. dimensione del carattere, una volta per nodo di testo
    var fatti = {};
    testi.concat(piedi).forEach(function (t) {
      if (fatti[t.id]) return; fatti[t.id] = 1;
      var cs = getComputedStyle(t.el), fs = parseFloat(cs.fontSize), peso = parseInt(cs.fontWeight, 10) || 400;
      var rel = fs / H * 100;
      if (rel < 1.4) rep.errori.push("Carattere illeggibile a proiettore (" + fs.toFixed(1) + "px = " + rel.toFixed(2) + "% dell'altezza): «" + t.testo + "»");
      else if (rel < 2.0) rep.avvisi.push("Carattere piccolo (" + fs.toFixed(1) + "px = " + rel.toFixed(2) + "% dell'altezza): «" + t.testo + "»");

      var colore = parse(cs.color), testoGradiente = false, coloriTesto;
      if (colore && colore[3] === 0) {
        for (var e = t.el; e && e.nodeType === 1; e = e.parentElement) {
          var ecs = getComputedStyle(e);
          if ((ecs.backgroundClip === "text" || ecs.webkitBackgroundClip === "text") && ecs.backgroundImage !== "none") {
            coloriTesto = coloriGradiente(ecs.backgroundImage); testoGradiente = e; break;
          }
        }
        if (!coloriTesto) return;
      } else coloriTesto = [colore];
      var basi = sfondi(testoGradiente || t.el, !!testoGradiente), op = opacita(t.el), peggiore = 99;
      coloriTesto.forEach(function (c) {
        basi.forEach(function (bg) {
          var cc = sopra([c[0], c[1], c[2], c[3] * op], bg);
          peggiore = Math.min(peggiore, ratio(cc, bg));
        });
      });
      var grande = fs >= 24 || (fs >= 18.66 && peso >= 700), soglia = grande ? 3 : 4.5;
      if (peggiore < soglia)
        rep.errori.push("Contrasto " + peggiore.toFixed(2) + ":1 sotto la soglia " + soglia + ":1: «" + t.testo + "»");
    });

    // 5. Densità (il controllo sul tempo di lettura è in Python, con data-secondi)
    if (rep.parole > 100) rep.avvisi.push("Slide densa: " + rep.parole + " parole. Taglia: il pubblico ascolta, non legge.");
    return rep;
  }

  function esegui() {
    var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
    var piede = document.querySelector(".chrome");
    var W = innerWidth, H = innerHeight;
    var rapporto = { viewport: [W, H], slides: [] };
    var m = location.hash.match(/^#slide=(\d+)$/);
    function attiva(i) {
      if (typeof vai === "function") vai(i);
      else slides.forEach(function (s, j) { s.classList.toggle("attiva", i === j); });
    }
    if (m) { attiva(parseInt(m[1], 10) - 1); return; }
    slides.forEach(function (s, i) { attiva(i); rapporto.slides.push(misuraSlide(s, i, piede, W, H)); });
    attiva(0);
    var out = document.createElement("script");
    out.type = "application/json"; out.id = "__controllo";
    out.textContent = JSON.stringify(rapporto).replace(/</g, "\\u003c");
    document.body.appendChild(out);
  }
  if (document.readyState === "complete") esegui(); else addEventListener("load", esegui);
})();
"""


def trova_browser():
    for c in BROWSER_CANDIDATI:
        if os.path.isabs(c) and os.path.exists(c):
            return c
        if not os.path.isabs(c) and shutil.which(c):
            return shutil.which(c)
    sys.exit("Nessun Chrome o Edge trovato: installane uno o aggiungi il percorso a BROWSER_CANDIDATI.")


def prepara_copia(sorgente, cartella):
    html = sorgente.read_text(encoding="utf-8")
    base = '<base href="' + sorgente.parent.as_uri() + '/">'
    # Sostituzioni con funzione: la sonda contiene backslash che re.sub interpreterebbe.
    html = re.sub(r"<head>", lambda m: m.group(0) + base, html, count=1, flags=re.I)
    html = re.sub(r"</body>", lambda m: "<script>" + SONDA_JS + "</script>" + m.group(0), html, count=1, flags=re.I)
    copia = cartella / "presentazione_sonda.html"
    copia.write_text(html, encoding="utf-8")
    return copia


def lancia(browser, argomenti, url, timeout=60, tentativi=2):
    """Avvia il browser headless. Ogni tanto un'istanza non termina: la si chiude e si riprova."""
    for _ in range(tentativi):
        profilo = tempfile.mkdtemp(prefix="controlla-slide-")
        cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
               "--no-default-browser-check", "--disable-extensions", "--user-data-dir=" + profilo,
               "--virtual-time-budget=1500"] + argomenti + [url]
        try:
            return subprocess.run(cmd, capture_output=True, timeout=timeout).stdout.decode("utf-8", "replace")
        except subprocess.TimeoutExpired:
            continue
        finally:
            shutil.rmtree(profilo, ignore_errors=True)
    return ""


def calibra(browser, cartella):
    """In headless --window-size è la finestra esterna: misura quanto spazio si mangia la cornice."""
    prova = cartella / "calibra.html"
    prova.write_text("<body><script>document.body.setAttribute('data-vp', innerWidth + 'x' + innerHeight)</script></body>",
                     encoding="utf-8")
    dom = lancia(browser, ["--window-size=1280,720", "--dump-dom"], prova.as_uri())
    m = re.search(r'data-vp="(\d+)x(\d+)"', dom)
    return (1280 - int(m.group(1)), 720 - int(m.group(2))) if m else (0, 0)


def misura(browser, copia, w, h):
    dom = lancia(browser, ["--window-size=%d,%d" % (w, h), "--dump-dom"], copia.as_uri())
    m = re.search(r'<script type="application/json" id="__controllo">(.*?)</script>', dom, re.S)
    if not m:
        return {"viewport": [w, h], "errore": "La sonda non ha prodotto un referto: la pagina ha un errore JavaScript?"}
    return json.loads(m.group(1))


def scatta(browser, copia, w, h, n, cartella):
    file = cartella / ("slide%02d_%dx%d.png" % (n, w, h))
    lancia(browser, ["--window-size=%d,%d" % (w, h), "--screenshot=" + str(file)], copia.as_uri() + "#slide=%d" % n)
    return file if file.exists() else None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", default="presentation/index.html")
    ap.add_argument("--risoluzioni", default="1280x720,1366x768,1920x1080")
    ap.add_argument("--screenshot", nargs="?", const="1280x720", default=None, metavar="RISOLUZIONI",
                    help="salva un PNG per slide (default 1280x720, il caso più stretto)")
    ap.add_argument("--budget", type=float, default=180, help="secondi di parola prima della demo")
    ap.add_argument("--json", action="store_true", help="stampa il referto grezzo in JSON")
    args = ap.parse_args()

    sorgente = pathlib.Path(args.file).resolve()
    if not sorgente.exists():
        sys.exit("File non trovato: %s" % sorgente)
    browser = trova_browser()
    cartella = pathlib.Path(tempfile.gettempdir()) / "controlla-slide"
    shutil.rmtree(cartella, ignore_errors=True)
    cartella.mkdir(parents=True)
    copia = prepara_copia(sorgente, cartella)
    def leggi(s):
        return [tuple(int(x) for x in r.lower().split("x")) for r in s.split(",")]
    risoluzioni = leggi(args.risoluzioni)
    dw, dh = calibra(browser, cartella)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        referti = list(pool.map(lambda r: misura(browser, copia, r[0] + dw, r[1] + dh), risoluzioni))
        nslide = max((len(r.get("slides", [])) for r in referti), default=0)
        foto = []
        if args.screenshot:
            lavori = [(w, h, n) for (w, h) in leggi(args.screenshot) for n in range(1, nslide + 1)]
            # In modalità screenshot la finestra headless non ha cornice: niente calibrazione.
            foto = list(pool.map(lambda j: scatta(browser, copia, j[0], j[1], j[2], cartella), lavori))

    if args.json:
        print(json.dumps(referti, ensure_ascii=False, indent=2))
        return 0

    errori_tot = avvisi_tot = 0
    for r in referti:
        w, h = r["viewport"]
        print("\n=== %dx%d ===" % (w, h))
        if "errore" in r:
            print("  ERRORE  " + r["errore"]); errori_tot += 1; continue
        for s in r["slides"]:
            stato = "OK" if not s["errori"] else "%d errori" % len(s["errori"])
            print("  [%d] %s — %d parole, sfondo %s — %s" % (s["n"], s["titolo"][:60], s["parole"], s["sfondo"], stato))
            for e in dict.fromkeys(s["errori"]):
                print("      ERRORE  " + e)
            for a in dict.fromkeys(s["avvisi"]):
                print("      avviso  " + a)
            errori_tot += len(s["errori"]); avvisi_tot += len(s["avvisi"])

    # Tempo: somma data-secondi delle slide che precedono quella con data-demo.
    if referti and "slides" in referti[0]:
        slides = referti[0]["slides"]
        idx_demo = next((i for i, s in enumerate(slides) if s.get("demo")), None)
        parlate = slides if idx_demo is None else slides[:idx_demo]
        senza = [s["n"] for s in parlate if s["secondi"] is None]
        totale = sum(s["secondi"] or 0 for s in parlate)
        print("\n=== Tempo di parola prima della demo ===")
        if idx_demo is None:
            print("  avviso  Nessuna slide con data-demo: sommo tutte le slide."); avvisi_tot += 1
        else:
            print("  La demo è la slide %d." % slides[idx_demo]["n"])
        if senza:
            print("  avviso  Slide senza data-secondi: %s. Non posso verificare il budget." % senza); avvisi_tot += 1
        # Un adulto legge in silenzio circa 4 parole al secondo (~240 al minuto): oltre,
        # la slide resta a schermo meno del tempo che serve per leggerla.
        for s in parlate:
            if s["secondi"] and s["parole"] / s["secondi"] > 4:
                print("  avviso  Slide %d: %d parole in %ds, non c'è il tempo di leggerle." % (s["n"], s["parole"], s["secondi"]))
                avvisi_tot += 1
        print("  Totale dichiarato: %ds su un budget di %ds." % (totale, args.budget))
        if totale > args.budget:
            print("  ERRORE  Il discorso sfora il budget di %ds." % (totale - args.budget)); errori_tot += 1

    if foto:
        mancanti = sum(1 for f in foto if f is None)
        print("\nScreenshot in %s (%d file%s)" % (cartella, len(foto) - mancanti,
                                                  ", %d non riusciti" % mancanti if mancanti else ""))
    print("\n%s — %d errori, %d avvisi" % ("=== TUTTO OK ===" if errori_tot == 0 else "=== DA CORREGGERE ===", errori_tot, avvisi_tot))
    return 1 if errori_tot else 0


if __name__ == "__main__":
    sys.exit(main())
