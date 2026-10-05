# Struttura agentica di VoceAmica

Tutto ciò che è servito per costruire VoceAmica con Claude Code, e i due agenti che
girano dentro il prodotto. Strumento usato: **Claude Code** (CLI ed estensione VS Code).

## Mappa

| Categoria | Dove | Cosa contiene |
|---|---|---|
| **Istruzioni** | [`CLAUDE.md`](CLAUDE.md) | Vincoli di stack, la regola «il modello sceglie, il codice conferma», come si scrive per Mario, confini |
| **Agenti** | [`claude-code/agents/`](claude-code/agents/) | Quattro sottoagenti: `data-curator`, `ui-anziani`, `revisore`, `revisore-slide` |
| **Comandi** | [`claude-code/commands/`](claude-code/commands/) | `/verifica-flussi` (prove end-to-end + anti-allucinazione), `/controlla-grounding` (verifica statica) |
| **Skills** | [`claude-code/skills/`](claude-code/skills/) | `accenture-pptx`: brand Accenture · `controlla-slide`: verifica che le slide si leggano al proiettore |
| **Prompt** | [`prompts/`](prompts/) | Il brief iniziale, invariato, e la descrizione dei prompt di prodotto |
| **Workflow** | [`WORKFLOW.md`](WORKFLOW.md) | Come è nato il progetto, divisione del lavoro, dove ha contribuito l'AI, dove è servita revisione umana |

Dettaglio di agenti, comandi e skill in [`claude-code/README.md`](claude-code/README.md).

## Il flusso, in breve

```
brief-iniziale.md ──► due agenti di pianificazione con obiettivi opposti
                      (rischio demo vs criteri di valutazione)
                              │
                              ▼  revisione umana: «il modello inventa i dati»
                         CLAUDE.md  (regola: il modello sceglie, il codice conferma)
                              │
          ┌───────────────────┼────────────────────┐
          ▼                   ▼                    ▼
    data-curator         ui-anziani        build di app.js
    app/data.js          app/index.html    (sessione principale)
          │                   │                    │
          └───────────────────┼────────────────────┘
                              ▼
          /controlla-grounding  ·  app/test.html  ·  /verifica-flussi
                              ▼
                     revisore  (prima del freeze)
```

## Agenti dentro il prodotto

| Ruolo | Prompt | Strumenti | Cosa produce |
|---|---|---|---|
| **VoceAmica** | `buildSystemPrompt` in [`app/data.js`](../app/data.js) | `conferma_prenotazione` | La conversazione con Mario |
| **Archivista** | `buildPromptArchivista` in [`app/data.js`](../app/data.js) | nessuno | La scheda di memoria in markdown, leggibile e cancellabile da Mario |

## Dove vivono questi file durante il lavoro

Claude Code legge le istruzioni da posizioni fisse. Questa cartella ne è la copia per
la consegna; nel repository sono attive anche in:

```
CLAUDE.md          = agents/CLAUDE.md
.claude/agents/    = agents/claude-code/agents/
.claude/commands/  = agents/claude-code/commands/
.claude/skills/    = agents/claude-code/skills/controlla-slide/
```
