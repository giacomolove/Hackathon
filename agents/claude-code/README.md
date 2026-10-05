# Configurazione agentica usata durante il build

Questi sono i file di configurazione con cui è stata costruita VoceAmica, raccolti qui
per la consegna. Nel repository di lavoro vivono nelle posizioni che Claude Code legge
automaticamente:

```
CLAUDE.md                      ← ../CLAUDE.md
.claude/agents/data-curator.md ← agents/data-curator.md
.claude/agents/ui-anziani.md   ← agents/ui-anziani.md
.claude/agents/revisore.md     ← agents/revisore.md
.claude/agents/revisore-slide.md ← agents/revisore-slide.md
.claude/skills/controlla-slide/  ← skills/controlla-slide/
.claude/commands/*.md          ← commands/
```

## Istruzioni di progetto

[`../CLAUDE.md`](../CLAUDE.md) — vincoli di stack, la regola «il modello sceglie, il
codice conferma», il registro linguistico per Mario e i confini su diagnosi e consulenza.
Scritta al minuto 10 del build, non alla fine: serviva a indirizzare il lavoro, non a
documentarlo a posteriori.

## Sottoagenti

| Agente | A cosa serve |
|---|---|
| [`data-curator`](agents/data-curator.md) | Presidia `app/data.js`. Scrive documenti amministrativi verosimili e impedisce che dati di dominio finiscano nel codice |
| [`ui-anziani`](agents/ui-anziani.md) | Presidia l'interfaccia. Progetta per un utente di 72 anni e rifiuta le modifiche che non fanno guadagnare autonomia |
| [`revisore`](agents/revisore.md) | Rivede il codice, corregge i bug che riesce a confermare e produce un referto con verdetto, correzioni e migliorie proposte. Da lanciare prima del freeze |
| [`revisore-slide`](agents/revisore-slide.md) | Rivede e corregge `presentation/index.html` perché si veda per intero al proiettore: niente testo tagliato o sovrapposto, contrasto sufficiente, tre minuti di parola prima della demo |

La separazione non è decorativa: i due agenti lavorano su file diversi, quindi possono
procedere in parallelo senza conflitti. È la stessa divisione che hanno seguito le due
persone del team.

## Comandi di verifica

| Comando | A cosa serve |
|---|---|
| [`/verifica-flussi`](commands/verifica-flussi.md) | Le cinque prove end-to-end, inclusa quella anti-allucinazione. Da eseguire prima di ogni commit |
| [`/controlla-grounding`](commands/controlla-grounding.md) | Verifica statica dell'invariante: nessun dato di dominio fuori da `data.js`, tool allineato agli slot, regole di prompt intatte |

`/controlla-grounding` esiste perché l'invariante del progetto è esattamente il tipo di
proprietà che si rompe in silenzio: basta una data scritta a mano in `app.js` durante una
correzione di fretta, e la difesa contro l'invenzione dei dati salta senza che nulla
segnali l'errore.

## Skill

| Skill | A cosa serve |
|---|---|
| [`accenture-pptx`](skills/accenture-pptx/SKILL.md) | Palette, tipografia e layout del brand Accenture, ripresi dalla presentazione HTML |
| [`controlla-slide`](skills/controlla-slide/SKILL.md) | Controllo automatico delle slide: testo tagliato o sovrapposto, contrasto, sfondo chiaro, durata del parlato prima della demo |

## Un agente dentro il prodotto: l'archivista

Gli agenti sopra servono a costruire VoceAmica. Dentro VoceAmica ne vive un secondo,
distinto da quello che parla con Mario.

A chiamata conclusa l'**archivista** riscrive la scheda della persona in markdown:
chi è, dove si blocca, cosa è stato concluso, cosa resta in sospeso. Non ha strumenti e
non conversa; produce solo un documento. Alla chiamata successiva quella scheda entra nel
prompt in un blocco `<MEMORIA>`, così Mario non deve ripetere quello che ha già detto.

Due scelte di progetto che vale la pena dichiarare:

- La memoria **non è una fonte di dati verificati**. Il prompt lo dice in modo esplicito:
  date, importi e codici validi restano solo quelli di `<DATI_VERIFICATI>`. Altrimenti una
  scheda imprecisa diventerebbe, alla telefonata dopo, un dato di fatto.
- La scheda è **in chiaro e revisionabile**. Mario la vede a schermo, la può scaricare e la
  può cancellare. È la forma più diretta di quello che il Tema 01 chiede quando domanda
  dove ha contribuito l'AI: non una dichiarazione, un documento leggibile.

Il prompt dell'archivista è in `app/data.js` (`buildPromptArchivista`), il ciclo in
`app/app.js` (`aggiornaScheda`).
