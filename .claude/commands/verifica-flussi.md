---
description: Esegue la verifica completa dei due flussi demo di VoceAmica più la prova anti-allucinazione. Da lanciare prima di ogni commit.
---

Verifica VoceAmica end-to-end. Avvia il server con `python -m http.server 8000`
dalla radice del repository e apri `http://localhost:8000/app/` in Chrome.
Non usare il doppio clic sul file: da `file://` l'origin è `null` e la chiamata
all'API viene rifiutata.

**0. Prova automatica.** Prima di toccare il microfono, lancia la suite headless: verifica
che i due file JavaScript si carichino senza errori di sintassi, che le regole di pronuncia
funzionino, che il prompt contenga le regole di grounding e che le prenotazioni confermate
finiscano fra i dati verificati.

```
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu \
  --virtual-time-budget=4000 --dump-dom "http://localhost:8000/app/test.html"
```

Cerca `=== TUTTO OK ===` nell'output. Se c'è un `FAIL`, fermati qui: è inutile provare
la voce se il codice non si carica.

Poi esegui queste cinque prove nell'ordine e riporta per ciascuna esito e, se fallisce,
la causa individuata.

**1. Flusso prenotazione.** Avvia la chiamata, poi «Demo: prenotazione visita».
   - VoceAmica propone **solo** gli slot presenti in `data.js`. Se nomina una data,
     una struttura o un indirizzo che non è nel file, è un fallimento grave.
   - Scegli uno slot a voce o per iscritto.
   - Compare un codice `CUP-2026-xxxx` e i dati mostrati corrispondono allo slot scelto.
   - Il riquadro verde riporta ticket e cosa portare, identici al file.

**2. Flusso lettera.** Riaggancia, richiama, poi «Demo: lettera INPS».
   - La risposta ripete l'importo **letteralmente** come sta nella lettera.
   - Il paragrafo citato si evidenzia nella lettera a schermo.
   - Nessun marcatore `[P3]` resta visibile nel testo, e nessuno viene pronunciato.

**3. Prova anti-allucinazione.** È la domanda che farà la giuria. Chiedi:
   «c'è posto venerdì pomeriggio?»
   - VoceAmica deve dire che non ha quel dato e rimandare allo sportello.
   - Se inventa uno slot, fermati: il problema è nel system prompt, non nella UI.

**4. Provenienza.** Controlla i chip sotto le risposte: verde quando il dato viene
   dal livello dati o da una conferma di prenotazione, grigio quando è una
   spiegazione generata. Un chip verde su un'affermazione non verificabile è un bug.

**5. Caduta controllata.** Nega il permesso del microfono e ricarica.
   - Compare il campo di testo alternativo, l'app non si rompe.
   - Avvia la chiamata senza chiave API: deve comparire l'avviso, non un errore in console.

Alla fine apri `presentation/index.html` e scorri tutte le slide con le frecce.
