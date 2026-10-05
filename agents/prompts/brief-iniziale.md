# VoceAmica — Assistente Telefonico AI per Anziani
**Hackathon Accenture × Unipol — Tema 01: Accessibilità Digitale**

---

## 0. Istruzioni per Claude Code

Costruisci l'intera applicazione seguendo questo documento dall'alto verso il basso, blocco per blocco. Non aggiungere feature non descritte qui. Ogni blocco è indipendente e testabile prima di passare al successivo.

**Stack obbligatorio:**
- Tutto in **un singolo file `index.html`** (HTML + CSS + JS inline)
- **Nessun framework, nessun build step, nessun npm**
- **Web Speech API** per input vocale (SpeechRecognition) e output vocale (SpeechSynthesis)
- **Anthropic Claude API** via fetch diretto (`https://api.anthropic.com/v1/messages`)
- La chiave API va inserita dall'utente in un campo nella UI al primo avvio — non hardcoded

---

## 1. Concept

**VoceAmica** è un assistente AI raggiungibile tramite una simulazione di chiamata telefonica nel browser.

L'anziano clicca "Chiama VoceAmica", parla normalmente ad alta voce, e l'assistente risponde a voce — come una telefonata con una persona paziente e competente. L'assistente conosce già chi è l'utente (profilo precaricato) e può agire per lui: prenotare visite, spiegare lettere burocratiche, guidarlo su pratiche INPS.

**Non è un chatbot. È una telefonata.**

---

## 2. Profilo utente — Mario Ferretti (mock)

Questo JSON rappresenta il "fascicolo digitale" di Mario. Usalo come contesto fisso nel system prompt di ogni chiamata Claude API.

```json
{
  "nome": "Mario Ferretti",
  "eta": 72,
  "codice_fiscale": "FRRMRA52D14F205Z",
  "citta": "Milano",
  "medico_base": "Dott.ssa Anna Carli — Studio via Mameli 8, Milano",
  "telefono": "333 4521876",
  "patologie": ["ipertensione lieve", "colesterolo alto"],
  "farmaci": ["Ramipril 5mg", "Rosuvastatina 10mg"],
  "storico_interazioni": [
    {
      "data": "2026-09-12",
      "tipo": "prenotazione",
      "descrizione": "Prenotata visita oculistica — 24 settembre 2026, Poliambulatorio Niguarda"
    },
    {
      "data": "2026-08-30",
      "tipo": "informazione",
      "descrizione": "Spiegazione lettera INPS su conguaglio pensione agosto"
    }
  ],
  "documenti_importanti": {
    "tessera_sanitaria_scadenza": "2027-03-15",
    "numero_pensione": "IT2340012345678"
  }
}
```

---

## 3. System prompt per Claude API

Usa questo system prompt esatto in ogni chiamata API. Non modificarlo, non accorciarlo.

```
Sei VoceAmica, un assistente vocale per Mario Ferretti, 72 anni.
Parli con Mario esattamente come farebbe un figlio paziente e competente al telefono.

REGOLE DI COMUNICAZIONE:
- Frasi corte. Mai più di 2 frasi consecutive.
- Zero termini burocratici: se devi usarne uno, spiegalo subito dopo.
- Tono caldo, mai condiscendente. Mai "lei" — usa sempre "tu".
- Quando Mario chiede di fare qualcosa (prenotare, scoprire, cercare), descrivi l'azione come se la stessi davvero facendo ("sto cercando adesso...", "ho trovato tre date disponibili...").
- Proponi sempre UN SOLO passo successivo alla volta.
- Se non capisci qualcosa, chiedi di ripetere in modo gentile.

PROFILO MARIO:
[inserisci qui il JSON del profilo]

CAPACITÀ SIMULATE (rispondi come se le facessi davvero):
- Prenotare visite mediche sul CUP regionale lombardo
- Spiegare lettere e comunicazioni di INPS, Agenzia delle Entrate, ASL
- Aiutare con pratiche online: ISEE, bonus, cambio medico
- Leggere e spiegare referti medici in linguaggio semplice
- Prenotare appuntamenti allo sportello dei servizi pubblici

NON fare mai:
- Diagnosi mediche
- Consigli su farmaci
- Consulenza legale o fiscale
- Promesse su tempi o esiti reali
```

---

## 4. Layout UI — specifica dettagliata

### 4.1 Struttura pagina (due colonne su desktop, una su mobile)

```
┌─────────────────────────────────────────────────────────┐
│  COLONNA SINISTRA (35%)     │  COLONNA DESTRA (65%)     │
│                             │                           │
│  [Scheda Mario]             │  [Simulatore chiamata]    │
│  - Foto avatar              │  - Stato chiamata         │
│  - Nome e età               │  - Transcript live        │
│  - Medico di base           │  - Bottone CHIAMA/RIAGGANCIA│
│  - Farmaci                  │  - Waveform animata       │
│  - Storico ultime 2         │                           │
│    interazioni              │                           │
│                             │                           │
│  [Setup API Key]            │                           │
│  (campo nascondibile)       │                           │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Colori e stile

- Sfondo: `#f0f4f8` (grigio chiarissimo, non bianco puro — meno affaticante)
- Accent principale: `#2563eb` (blu — trasmette fiducia, tipico dei servizi pubblici)
- Scheda Mario: bianco, bordo arrotondato, ombra leggera
- Font: system-ui, dimensione base **18px** (non 16px — è per anziani)
- Bottoni: padding generoso, min-height 56px, testo grande

### 4.3 Simulatore chiamata — stati visivi

**STATO IDLE** — nessuna chiamata in corso
- Illustrazione semplice di un telefono
- Testo: "Premi il pulsante verde per chiamare VoceAmica"
- Bottone verde grande: "📞 Chiama VoceAmica"

**STATO IN CHIAMATA — MARIO PARLA** (SpeechRecognition attivo)
- Cerchio animato pulsante azzurro
- Testo: "🎤 Mario sta parlando..."
- Trascrizione in tempo reale del parlato sotto
- Bottone rosso: "🔴 Riaggancia"

**STATO IN CHIAMATA — ASSISTENTE RISPONDE** (SpeechSynthesis attivo)
- Cerchio animato pulsante verde
- Testo: "🔊 VoceAmica sta rispondendo..."
- Testo della risposta visibile (grande, leggibile)
- Bottone rosso: "🔴 Riaggancia"

**STATO ELABORAZIONE** (chiamata API in corso)
- Spinner semplice
- Testo: "⏳ Sto cercando..."

### 4.4 Storico sessione

Sotto il simulatore: lista scrollabile delle ultime battute della chiamata in corso, in formato "bolla chat" (Mario a destra, VoceAmica a sinistra). Font 16px minimo.

---

## 5. Logica applicativa — flusso completo

```
1. Utente inserisce API key → salvata in memoria (non localStorage)
2. Utente clicca "Chiama VoceAmica"
3. → Avvia SpeechRecognition (lingua: it-IT)
4. → VoceAmica dice a voce: "Ciao Mario! Sono VoceAmica. Come posso aiutarti oggi?"
5. → Stato: MARIO PARLA
6. Mario parla → transcript catturato su silence/pause
7. → Stato: ELABORAZIONE
8. → Chiamata Claude API con: system prompt + profilo Mario + intera history conversazione + ultimo messaggio Mario
9. → Risposta Claude ricevuta
10. → Stato: ASSISTENTE RISPONDE
11. → SpeechSynthesis legge la risposta (voce: it-IT, rate: 0.85, pitch: 1.0)
12. → Risposta aggiunta alla history e alle bolle visive
13. → Torna al punto 3 (Mario può riparlare)
14. "Riaggancia" → ferma tutto, mostra riepilogo chiamata
```

---

## 6. I due flussi demo — script esatti

Questi sono i due scenari che verranno mostrati alla giuria. Il sistema deve gestirli naturalmente, ma prepara anche dei **"quick launch"** button nella UI che pre-caricano il primo messaggio come se Mario lo avesse detto — per velocizzare la demo.

### Flusso A — "Prenotare una visita cardiologica"

**Mario dice:** *"Vorrei prenotare una visita cardiologica, ma non so come fare"*

**VoceAmica risponde (atteso):** qualcosa come:
> "Certo Mario, ci penso io. Sto cercando adesso i cardiologi disponibili a Milano. Ho trovato tre date: martedì 14 ottobre alle 9:30 al Policlinico, giovedì 16 alle 10:00 all'Ospedale Niguarda, o lunedì 20 alle 15:00 al San Raffaele. Quale ti è più comoda?"

**Mario dice:** *"Martedì mattina va benissimo"*

**VoceAmica risponde:**
> "Perfetto. Ho prenotato per martedì 14 ottobre alle 9:30 al Policlinico di Milano, padiglione cardiologia, ingresso da via Sforza. Ti mando un SMS di conferma al 333 4521876. Porta con te la tessera sanitaria e l'impegnativa della dottoressa Carli. C'è altro che ti serve?"

### Flusso B — "Lettera incomprensibile dall'INPS"

**Mario dice:** *"Mi è arrivata una lettera dall'INPS, non capisco cosa vogliono. Parla di conguaglio e di una somma da restituire"*

**VoceAmica risponde (atteso):**
> "Capisco, queste lettere sono spesso scritte in modo complicato. Ti spiego. Il conguaglio INPS è un ricalcolo della pensione che fanno ogni anno. A volte risulta che durante l'anno ti hanno pagato un po' di più — e allora chiedono di restituire la differenza. Non è una multa, è solo una correzione. Quanto dice la lettera che dovresti restituire?"

**Mario dice:** *"Dice 340 euro"*

**VoceAmica risponde:**
> "340 euro. Di solito l'INPS trattiene quella cifra direttamente dalla pensione nei mesi successivi, un po' alla volta — non devi fare niente tu. Ma per essere sicuri, ti conviene chiamare il numero verde INPS: 803 164, è gratuito. Vuoi che ti aiuti a capire cos'altro dice la lettera?"

---

## 7. Quick Launch buttons (per la demo)

Aggiungi nell'interfaccia — solo visibile durante la chiamata — due bottoni piccoli:

- `[Demo: Prenotazione visita]` → inietta il testo "Vorrei prenotare una visita cardiologica, ma non so come fare" come se Mario lo avesse detto, avvia il flusso
- `[Demo: Lettera INPS]` → inietta il testo "Mi è arrivata una lettera dall'INPS, non capisco cosa vogliono"

Questi sono salvavita durante la demo live se il riconoscimento vocale fa i capricci.

---

## 8. Gestione errori — essenziale

| Situazione | Comportamento |
|---|---|
| API key mancante | Alert visivo: "Inserisci la chiave API per iniziare" |
| SpeechRecognition non supportato | Mostra campo testo alternativo per scrivere |
| Errore chiamata Claude API | VoceAmica dice a voce: "Scusa Mario, ho avuto un problema. Riprova tra un momento." |
| Silenzio troppo lungo | Dopo 8 secondi: "Mario, sei ancora lì? Dimmi pure quando sei pronto." |
| Browser non supporta SpeechSynthesis | Mostra solo testo, nessun crash |

---

## 9. Parametri chiamata Claude API

```javascript
{
  model: "claude-sonnet-4-6",
  max_tokens: 300,           // Risposte brevi obbligatorie
  messages: conversationHistory,  // Array completo della sessione
  system: SYSTEM_PROMPT      // System prompt con profilo Mario incluso
}
```

**Importante:** `max_tokens: 300` è intenzionale. Risposte lunghe uccidono l'esperienza vocale.

---

## 10. Presentazione finale — `presentazione.html`

Crea un **secondo file separato** `presentazione.html` con 5 slide in formato fullscreen (navigazione con frecce o click).

### Slide 1 — Il problema
- Titolo grande: **"8 milioni di anziani italiani esclusi dai servizi digitali"**
- 3 bullet semplici: non sanno usare SPID / non capiscono i moduli / nessuno li aiuta
- Immagine/icona: telefono analogico vs schermo confuso

### Slide 2 — La persona
- Nome: **Mario Ferretti, 72 anni, Milano**
- Foto avatar
- Citazione: *"Mio figlio mi ha detto di farlo online. Ma io non ci capisco niente."*
- Il suo obiettivo oggi: prenotare una visita cardiologica

### Slide 3 — La soluzione
- Titolo: **VoceAmica — chiami come chiameresti tuo figlio**
- Schema visivo semplice: Mario parla → VoceAmica capisce → VoceAmica agisce
- 3 elementi chiave: Voce / Memoria / Azione

### Slide 4 — La demo
- Slide nera con testo bianco grande: **"DEMO LIVE"**
- Sotto: "Mario chiama. Vuole prenotare una visita."
- (Qui il presentatore apre l'app)

### Slide 5 — Risultato e limiti
- **Autonomia guadagnata:** Mario completa da solo task che richiedevano l'aiuto di un familiare
- **Cosa è stato semplificato:** linguaggio, canale (voce invece di UI), memoria del contesto
- **Limiti onesti:** le prenotazioni sono simulate / richiede connessione internet / riconoscimento vocale dipende dal browser
- **Prossimo passo:** integrazione reale CUP Lombardia via API pubblica

---

## 11. Struttura file da consegnare su GitHub

```
/
├── index.html          ← app principale (tutto qui)
├── presentazione.html  ← slide della presentazione
└── README.md           ← 10 righe: cos'è, come si usa, come si avvia
```

**README.md minimo:**
```markdown
# VoceAmica
Assistente vocale AI per anziani — Hackathon Accenture 2026

## Come usare
1. Apri `index.html` in Chrome o Edge (Safari non supporta SpeechRecognition)
2. Inserisci la tua chiave API Anthropic nel campo in alto a sinistra
3. Clicca "Chiama VoceAmica" e parla

## Presentazione
Apri `presentazione.html` — naviga con le frecce o cliccando

## Stack
HTML + CSS + JavaScript vanilla · Web Speech API · Anthropic Claude API
```

---

## 12. Ordine di build — rispettalo

1. **Struttura HTML** e layout due colonne con scheda Mario hardcoded
2. **Bottone chiama** + stati visivi (idle / in chiamata / elaborazione) — senza API
3. **Web Speech API** — riconoscimento vocale funzionante, mostra transcript
4. **SpeechSynthesis** — risposta vocale con testo hardcoded di test
5. **Claude API** — integrazione reale, sostituisce il testo hardcoded
6. **Quick launch buttons** per i due flussi demo
7. **Gestione errori** basilare
8. **Presentazione.html**
9. **README.md**
10. Test end-to-end dei due flussi, bug fix

---

*Documento generato per Hackathon Accenture Application Engineering — 05 ottobre 2026*
*Tema 01: Accessibilità Digitale · VoceAmica*
