# Struttura agentica e contributo dell'AI

Documento doppio: descrive la struttura agentica richiesta dalle regole di consegna, e
soddisfa il vincolo del Tema 01 *«indicare dove l'AI ha contribuito e dove è stata
necessaria revisione umana»*.

## 1. Come è nato il progetto

Il percorso non è partito dal codice ma dalla scelta del problema.

1. **Esplorazione del tema.** Partendo dal Tema 01 e dall'ipotesi «anziani e servizi
   digitali», abbiamo generato quindici combinazioni di persona + servizio + barriera
   (SPID, CUP, PagoPA, ISEE, home banking, cartelle esattoriali…) e le abbiamo valutate
   su un solo criterio: *quanto è corto e visibile il momento di blocco?* Un flusso con un
   unico punto di rottura si dimostra in tre minuti; uno con dieci passaggi no.
2. **Scelta.** Prenotazione CUP e lettera INPS, perché condividono la stessa persona e
   lo stesso tipo di barriera (gergo amministrativo) con due esiti diversi: un'azione
   da completare e un documento da capire.
3. **Brief.** Abbiamo scritto il brief funzionale completo prima di aprire un editor.
   È conservato invariato in [`prompts/brief-iniziale.md`](prompts/brief-iniziale.md).
4. **Progettazione in parallelo.** Due agenti di pianificazione indipendenti sullo stesso
   brief, con prospettive deliberatamente opposte: uno incaricato di minimizzare il rischio
   di non arrivare alla demo, l'altro di massimizzare l'aderenza ai criteri di valutazione.
   Il piano finale è la sintesi dei due.
5. **Implementazione** secondo il piano, con verifica continua.

Il punto 4 è ciò che ha prodotto la decisione più importante del progetto, descritta sotto.

## 2. La decisione che ha cambiato il progetto

Il brief iniziale istruiva il modello a «rispondere come se facesse davvero» le azioni.
Negli script di esempio il modello produceva da sé tre date con ospedali di Milano,
padiglioni, numeri verdi e importi.

L'agente incaricato della valutazione l'ha classificato come rischio di punteggio, non
come dettaglio implementativo: il Tema 01 impone *«semplificare senza tradire»* ed esclude
*«uso dell'AI non spiegabile dal team»*. Una giuria tecnica smonta una demo così con una
domanda sola — «queste date da dove arrivano?».

Da qui sono nati il livello dati deterministico (`app/data.js`), il tool unico sull'unica
azione che scrive, e il meccanismo di tracciabilità con i marcatori di paragrafo.

**Il modello sceglie, il codice conferma.**

## 3. Divisione del lavoro

Criterio: separare per file, così che due flussi di lavoro non tocchino mai le stesse righe.

| Ambito | File | Responsabilità |
|---|---|---|
| Interfaccia e motore di chiamata | `app/index.html`, `app/app.js` | Layout per utente anziano, macchina a stati, Web Speech, chiamata API, giro di tool use |
| Dati e testi amministrativi | `app/data.js` | Slot CUP, testo della lettera, contatti, limiti, system prompt |
| Presentazione | `presentation/index.html` | Slide, brand Accenture |

I file di configurazione effettivamente usati durante il build sono in
[`claude-code/`](claude-code/): le istruzioni di progetto, i sottoagenti e i comandi
ripetibili di verifica.

## 4. Dove ha contribuito l'AI

- **Generazione delle ipotesi di partenza.** Le quindici combinazioni persona/servizio/barriera.
- **Pianificazione in prospettive contrapposte.** Il confronto fra due piani indipendenti,
  che ha fatto emergere il rischio sul grounding.
- **Scrittura del codice.** Interfaccia, macchina a stati, integrazione dell'API e
  livello di evidenza.
- **Stesura dei testi amministrativi verosimili.** La lettera INPS con il gergo,
  i riferimenti normativi e la struttura di una comunicazione reale.
- **In esecuzione, dentro il prodotto.** Comprensione del linguaggio naturale di Mario,
  riformulazione in italiano semplice, scelta di quale slot proporre e quale paragrafo citare.

## 5. Dove è stata necessaria revisione umana

Queste sono le correzioni che un umano ha dovuto imporre, e sono il motivo per cui il
progetto regge:

1. **Il brief faceva inventare i dati al modello.** Riconosciuto e corretto in fase di
   progettazione: è la decisione descritta al punto 2.
2. **Il modello indicato nel brief era di generazione precedente**, e il tetto di
   `max_tokens: 300` avrebbe troncato a metà il JSON della chiamata a funzione —
   un errore che si manifesta solo quando il tool viene invocato, cioè durante la demo.
3. **L'header CORS.** Senza `anthropic-dangerous-direct-browser-access: true` la
   chiamata dal browser non parte. Verificato prima di scrivere l'integrazione, non dopo.
4. **Il loop audio.** Il microfono cattura la voce sintetica dell'assistente e si innesca
   un ciclo. La soluzione — il microfono esiste solo nello stato di ascolto, e si distrugge
   invece di essere silenziato — è una scelta di progettazione, non un suggerimento emerso
   dal codice.
5. **La statistica di apertura della presentazione.** La prima stesura conteneva un numero
   plausibile ma non verificato. Sostituito con il dato Istat reale («Cittadini e ICT», 2025:
   il 72,5% delle persone fra 65 e 74 anni usa internet, solo il 27,4% ha competenze digitali
   di base). Sarebbe stato incoerente costruire un'architettura contro l'invenzione dei dati
   e poi aprire la presentazione con un dato inventato.
6. **I testi che Mario sente e legge.** Tono, lunghezza delle frasi e scelta delle parole
   sono stati riletti a mano: è la parte del prodotto che non si può delegare, perché è
   l'unica che l'utente percepisce davvero.

## 6. Cosa resta non verificato

Dichiarato per onestà: gli slot CUP e la lettera INPS sono **dati di esempio**, scritti per
essere verosimili. Non provengono da sistemi reali e non sono stati validati da un operatore
sanitario o previdenziale. Il prototipo non invia nulla a nessun sistema esterno.

## 7. Revisione prima del freeze

Tre sottoagenti lanciati in parallelo, ciascuno sul proprio ambito, con l'istruzione di
correggere solo ciò che riuscivano a dimostrare.

| Agente | Ha trovato | Esito |
|---|---|---|
| `data-curator` (`/controlla-grounding`) | I sei controlli statici passano. Ma i giorni della settimana degli slot erano quelli del 2025: il «giovedì 16 ottobre» era in realtà un venerdì, proprio il giorno della prova anti-allucinazione. Nelle slide c'erano numeri che non tornavano con l'app: 14 campi invece di 10, 3 riferimenti normativi invece di 2 | Date e slide corrette |
| `revisore` | Microfono che si riapriva dopo il riaggancio se l'API falliva. Timer del silenzio che interrompeva Mario mentre parlava. Prenotazioni salvate a chiamata chiusa. Marcatori `[P9]` di paragrafi inesistenti trattati come dati verificati | Sei bug corretti, verificati con `test.html` e con un banco di prova senza microfono |
| `ui-anziani` | Testi sotto i 14px. Pulsante verde con contrasto 3,3:1. «Cancella tutto» irreversibile e senza conferma. Stato della chiamata non annunciato ai lettori di schermo | Corretti; lasciate deliberatamente le due eccezioni dichiarate in `CLAUDE.md` |

Delle migliorie proposte ne sono state applicate tre, quelle che proteggono la demo
dal vivo: i marcatori multipli come `[P2, P3]`, gli asterischi visibili nelle bolle e
la risposta vuota dopo una prenotazione. Le altre non sono state applicate.

