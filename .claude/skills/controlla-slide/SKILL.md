---
name: controlla-slide
description: Controlla che le slide di presentation/index.html si vedano per intero al proiettore — niente testo tagliato o sovrapposto, contrasto sufficiente, sfondo chiaro, tre minuti di parola prima della demo. Da lanciare dopo ogni modifica alle slide e prima di presentare.
---

Le slide di VoceAmica si presentano in **circa 3 minuti, poi parte la demo**. Il pubblico
le vede una volta, da lontano, su un proiettore che non abbiamo provato. Questa skill
verifica quello che vede davvero, non quello che c'è nel codice.

## 1. Lancia il controllo

Dalla radice del repository:

```
python .claude/skills/controlla-slide/controlla_slide.py presentation/index.html --screenshot
```

Lo script apre la presentazione in Chrome (o Edge) headless a 1280×720, 1366×768 e
1920×1080, attiva una slide alla volta e misura:

| Controllo | Cosa segnala | Gravità |
|---|---|---|
| Testo tagliato | Righe fuori dallo schermo. Il body ha `overflow: hidden`, quindi quel testo è perso | ERRORE |
| Contenuto troppo alto | La slide è più alta dello schermo | ERRORE |
| Sovrapposizioni | Due testi che si coprono, incluso il piè di pagina fisso | ERRORE |
| Contrasto | Sotto 4.5:1 (3:1 per il testo grande), sfondi e trasparenze composti | ERRORE |
| Carattere | Sotto l'1,4% dell'altezza dello schermo è ERRORE, sotto il 2% avviso | ERRORE / avviso |
| Sfondo | Slide quasi nera: il team ha chiesto sfondi chiari | avviso |
| Tempo | Somma di `data-secondi` fino alla slide con `data-demo`: oltre 180 s | ERRORE |
| Lettura | Più di 4 parole al secondo previsto: la slide va via prima che la si legga | avviso |

Esce con codice 1 se c'è almeno un ERRORE. Opzioni utili: `--screenshot 1920x1080` per
fotografare un'altra risoluzione, `--budget 150` per un discorso più corto, `--json` per
il referto grezzo.

## 2. Guarda gli screenshot

Lo script stampa la cartella dei PNG. Aprili tutti con Read, uno per slide. Servono per
quello che lo script non misura:

- riquadri, bordi e forme tagliati o accavallati (lo script controlla solo il testo)
- gerarchia: il titolo si legge per primo? C'è un solo messaggio per slide?
- equilibrio: una colonna piena e l'altra vuota, o tutto schiacciato in alto

## 3. Correggi

Regole delle slide di VoceAmica:

- **Misure in `--u`**, l'unità di slide definita in `:root` (`min(1vw, 1.778vh)`). Niente `px`
  fissi per testo e spaziature: con `--u` la slide scala identica a ogni risoluzione.
- **Spazio per il piè di pagina.** Il padding basso della slide (6.5 u) tiene il contenuto
  sopra la barra fissa. Non ridurlo; se il contenuto non entra, taglia testo.
- **Sfondo chiaro** su tutte le slide, viola Accenture per accenti e titoli. Testo viola
  in `--viola-testo` (#7500C0), mai `#A100FF` su testo piccolo.
- **Tre minuti.** Ogni slide prima della demo ha `data-secondi`; la demo ha `data-demo`
  ed è l'ultima prima di «Grazie». Se sfori, togli parole, non secondi alle altre slide.
- **Taglia, non rimpicciolire.** Un testo che non entra si accorcia. Rimpicciolire il carattere
  sposta il problema dal layout alla leggibilità.
- **I fatti non si toccano.** Numeri e citazioni (72,5%, 27,4%, euro 340,00, passo 4 di 7) devono
  restare identici a `app/data.js` e alla fonte citata. Accorciare una frase è lecito;
  arrotondare un dato no.
- Nessuna risorsa esterna: niente CDN, niente font remoti, niente immagini da rete.

Poi rilancia lo script. Hai finito quando stampa `=== TUTTO OK ===` e gli screenshot
non mostrano nulla di storto.

## Limiti da dichiarare

- Lo script vede il **testo**, non le forme: una card che esce dallo schermo senza testo
  dentro passa inosservata. Per questo il passo 2 non è facoltativo.
- Il layout dipende dai **font installati**. Le slide chiedono Graphik e ripiegano su Inter
  e poi Segoe UI: se il PC della presentazione non ha Graphik, le righe cambiano lunghezza.
  Rilancia il controllo sul PC da cui si proietta.
- Il contrasto su gradienti è stimato sugli stop di colore, non pixel per pixel.
