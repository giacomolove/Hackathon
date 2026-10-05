# VoceAmica — istruzioni di progetto

Assistente vocale per Mario Ferretti, 72 anni, che non riesce a usare da solo il portale
CUP e non capisce le lettere dell'INPS. Hackathon Hagenthon, Tema 01 — Accessibilità Digitale.

## Vincoli di stack, non negoziabili

- Nessun framework, nessun build step, nessun npm. Solo HTML, CSS e JavaScript.
- Tre file in `app/`: `index.html`, `data.js`, `app.js`. `data.js` si carica prima di `app.js`.
- Tag `<script src>` semplici, **non** ES modules: devono funzionare anche senza bundler.
- Nessuna risorsa esterna: niente CDN, niente font remoti, niente immagini da rete.
  In sala la connessione può mancare e la demo deve partire comunque.
- Modello: `claude-haiku-4-5`. Non inviare `thinking` né `output_config.effort`
  (su Haiku l'effort è un errore, e senza thinking la risposta vocale parte subito).
- `max_tokens: 700`. Non scendere a 300: troncherebbe a metà il JSON di una chiamata a funzione.
- La chiamata all'API richiede l'header `anthropic-dangerous-direct-browser-access: true`,
  altrimenti il browser la blocca in CORS.

## La regola che governa tutto il resto

**Il modello sceglie, il codice conferma.**

Ogni data, orario, indirizzo, importo, numero di telefono e codice che VoceAmica pronuncia
deve esistere in `data.js`. Il modello può scegliere *quale* dato usare e *come* spiegarlo;
non può introdurne di nuovi.

Conseguenze operative:

- Non scrivere dati di dominio in `app.js` o dentro i prompt: vanno in `data.js`.
- La conferma di una prenotazione passa da `conferma_prenotazione()`, che è codice
  deterministico. Il modello non può dichiarare una prenotazione fatta da sé.
- Quando il modello spiega la lettera deve citare il paragrafo di origine con un
  marcatore `[P3]`. Il marcatore si rimuove prima della sintesi vocale e si usa per
  evidenziare il paragrafo nel documento originale.
- Importi, date e scadenze si ripetono letterali. Mai arrotondati, mai parafrasati.

## Come si scrive per Mario

- Frasi corte, mai più di due di seguito. Un solo passo successivo alla volta.
- Dare del tu. Mai «lei», mai tono condiscendente.
- Zero termini burocratici; se un termine è inevitabile, spiegarlo subito dopo.
- Nell'interfaccia: testo base 18px, pulsanti alti almeno 56px, nessun elemento
  che richieda precisione di puntamento.
- Niente pannelli di debug, niente JSON a schermo, niente gergo tecnico nella UI.
  Lo strumento è per Mario, non per noi.
- Due eccezioni deliberate alla regola delle dimensioni, da non "correggere":
  la replica del portale nella scheda «come fa Mario oggi», dove il carattere piccolo
  è il problema che stiamo mostrando; e i pulsanti «Demo», che sono appigli per chi
  presenta e non parte dell'interfaccia di Mario.

## Confini

Mai diagnosi mediche, consigli su farmaci, consulenza legale o fiscale. VoceAmica
spiega **cosa dice** un documento, non **cosa conviene fare**. I limiti stanno in
`LIMITI` e sono sempre visibili a schermo.

## Verifica prima di ogni commit

Esegui `/verifica-flussi`. Nessun commit se la prova anti-allucinazione non passa:
a «c'è posto venerdì pomeriggio?» VoceAmica deve dire che quel dato non ce l'ha,
non inventare uno slot.
