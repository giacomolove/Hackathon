# VoceAmica

Assistente vocale per anziani — Hackathon Hagenthon, Accenture Application Engineering
Tema 01: Accessibilità Digitale

Mario Ferretti ha 72 anni e si ferma al passo 4 di 7 del portale CUP, dove gli vengono
chiesti la branca specialistica, il codice prestazione e la classe di priorità.
Con VoceAmica non compila niente: preme un pulsante verde e parla, come se chiamasse
suo figlio. L'assistente capisce, agisce e gli restituisce un codice di prenotazione.

## Come si usa

1. Avvia un server locale dalla radice del repository:
   ```
   python -m http.server 8000
   ```
2. Apri **`http://localhost:8000/app/`** in Chrome o Edge.
   Non aprire il file con un doppio clic: da `file://` la chiamata all'API viene
   rifiutata, e Safari non supporta il riconoscimento vocale.
3. In «Accesso», nella colonna di sinistra, incolla la tua chiave API Anthropic.
   Resta solo in memoria.
4. Premi **Chiama VoceAmica** e parla. I due pulsanti «Demo» avviano i flussi
   di esempio se il microfono fa i capricci.

La scheda **«Come fa Mario oggi»** mostra il percorso che deve affrontare senza
VoceAmica: la replica del portale e la lettera originale dell'INPS.

## Struttura

```
app/              il prototipo
  index.html        interfaccia (chiamata + «Come fa Mario oggi»)
  data.js           unica fonte dei dati e dei prompt
  app.js            macchina a stati, voce, chiamata all'API, tool use
  test.html         prove automatiche, anche headless
agents/           la struttura agentica: indice in agents/README.md
  CLAUDE.md         istruzioni di progetto
  WORKFLOW.md       come è nato, dove ha contribuito l'AI, dove è servita revisione umana
  claude-code/      sottoagenti, comandi, skill
  prompts/          brief iniziale e prompt di prodotto
presentation/     index.html (frecce o clic per navigare)
```

## Dove trovare cosa

| Richiesto | Dove |
|---|---|
| Soluzione sviluppata | [`app/`](app/) |
| Agenti, istruzioni, comandi, prompt, skill, workflow | [`agents/README.md`](agents/README.md) |
| Presentazione HTML, brand Accenture | [`presentation/index.html`](presentation/index.html) |
| Tema 01 · Persona & barriera | Slide 3 · scheda «Come fa Mario oggi» nell'app |
| Tema 01 · Percorso assistito, prima e dopo | Slide 5 e demo dal vivo · pulsanti «Demo» nell'app |
| Tema 01 · Autonomia & limiti | Slide 9 · riquadro «Limiti» sempre visibile nell'app |
| Dove ha contribuito l'AI, dove è servita revisione umana | [`agents/WORKFLOW.md`](agents/WORKFLOW.md) §4–5 |
| Semplificare senza tradire | Marcatori `[Pn]`, importi letterali, paragrafo evidenziato nella lettera originale |

## Prove

Con il server avviato:

```
chrome --headless=new --virtual-time-budget=4000 --dump-dom http://localhost:8000/app/test.html
```

Deve comparire `=== TUTTO OK ===`. Le prove dal vivo, compresa quella anti-allucinazione
(«c'è posto venerdì pomeriggio?» → «quel dato non ce l'ho»), sono in
[`agents/claude-code/commands/verifica-flussi.md`](agents/claude-code/commands/verifica-flussi.md).

## Come è fatta

**Il modello sceglie, il codice conferma.** Ogni data, indirizzo, importo e codice che
VoceAmica pronuncia esiste in [`app/data.js`](app/data.js); il modello può scegliere
quale usare e come spiegarlo, non introdurne di nuovi. Le prenotazioni passano da una
funzione deterministica, non da una frase generata. Quando spiega la lettera, cita il
paragrafo di origine e lo evidenzia nel documento originale, ripetendo gli importi
letteralmente.

Ogni risposta mostra la propria provenienza: *dato verificato* oppure *spiegazione
generata dall'AI, da confermare allo sportello*.

Dove ha contribuito l'AI e dove è servita revisione umana è documentato in
[`agents/WORKFLOW.md`](agents/WORKFLOW.md).

## Limiti

Le prenotazioni sono **simulate su dati di esempio**: non raggiungono il CUP reale e la
lettera non è un documento INPS autentico. VoceAmica non dà diagnosi, consigli su
farmaci, consulenza legale o fiscale: spiega cosa dice un documento, non cosa conviene
fare. Richiede una connessione a internet.

## Stack

HTML, CSS e JavaScript senza framework e senza build step · Web Speech API per voce in
ingresso e in uscita · API Anthropic (`claude-haiku-4-5`) chiamata direttamente dal browser.
