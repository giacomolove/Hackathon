/* VoceAmica — DATA LAYER
 *
 * DATI DI ESEMPIO. Non provengono da sistemi reali: gli slot non sono
 * disponibilità effettive del CUP Lombardia e la lettera non è un documento
 * INPS autentico. Sono scritti per essere verosimili.
 * Anche Mario è un personaggio inventato: il codice fiscale è volutamente non valido,
 * perché uno valido potrebbe appartenere a una persona reale. CONTATTI riporta i
 * recapiti pubblici degli enti, da ricontrollare prima di qualunque uso reale.
 *
 * Regola dell'architettura: il modello SCEGLIE fra questi dati, non ne inventa
 * altri. Tutto ciò che VoceAmica afferma come fatto deve esistere in questo file.
 */

const MARIO = {
  nome: "Mario Ferretti",
  eta: 72,
  codice_fiscale: "FRRMRA52D14F205Z",
  citta: "Milano",
  medico_base: "Dott.ssa Anna Carli — Studio via Mameli 8, Milano",
  telefono: "333 4521876",
  patologie: ["ipertensione lieve", "colesterolo alto"],
  farmaci: ["Ramipril 5mg", "Rosuvastatina 10mg"],
  storico_interazioni: [
    {
      data: "2026-09-12",
      tipo: "prenotazione",
      descrizione: "Prenotata visita oculistica — 24 settembre 2026, Poliambulatorio Niguarda"
    },
    {
      data: "2026-08-30",
      tipo: "informazione",
      descrizione: "Spiegazione lettera INPS su conguaglio pensione agosto"
    }
  ],
  documenti_importanti: {
    tessera_sanitaria_scadenza: "2027-03-15",
    numero_pensione: "IT2340012345678"
  },
  // La barriera, datata e puntuale. Deliverable 01.
  barriera: "Si blocca al passo 4 di 7 del portale CUP: deve scegliere branca specialistica, codice prestazione e classe di priorità, campi di cui non conosce il significato."
};

/* ---------------------------------------------------------------- CUP ---- */

const CUP_SLOTS = [
  {
    id: "SLOT-1",
    data: "martedì 13 ottobre 2026",
    ora: "09:30",
    struttura: "Policlinico di Milano",
    reparto: "Cardiologia, padiglione Zonda",
    indirizzo: "Via Francesco Sforza 35, Milano",
    prestazione: "Visita cardiologica di primo accesso",
    codice_prestazione: "89.7B.4",
    classe_priorita: "D — differibile (entro 30 giorni)",
    ticket: "23,30 euro",
    cosa_portare: ["Tessera sanitaria", "Impegnativa della dott.ssa Carli", "Documento d'identità"]
  },
  {
    id: "SLOT-2",
    data: "giovedì 15 ottobre 2026",
    ora: "10:00",
    struttura: "ASST Grande Ospedale Metropolitano Niguarda",
    reparto: "Cardiologia, blocco Sud piano 2",
    indirizzo: "Piazza dell'Ospedale Maggiore 3, Milano",
    prestazione: "Visita cardiologica di primo accesso",
    codice_prestazione: "89.7B.4",
    classe_priorita: "D — differibile (entro 30 giorni)",
    ticket: "23,30 euro",
    cosa_portare: ["Tessera sanitaria", "Impegnativa della dott.ssa Carli", "Documento d'identità"]
  },
  {
    id: "SLOT-3",
    data: "lunedì 19 ottobre 2026",
    ora: "15:00",
    struttura: "IRCCS Ospedale San Raffaele",
    reparto: "Cardiologia, ambulatorio 4",
    indirizzo: "Via Olgettina 60, Milano",
    prestazione: "Visita cardiologica di primo accesso",
    codice_prestazione: "89.7B.4",
    classe_priorita: "D — differibile (entro 30 giorni)",
    ticket: "23,30 euro",
    cosa_portare: ["Tessera sanitaria", "Impegnativa della dott.ssa Carli", "Documento d'identità"]
  }
];

/* -------------------------------------------------------------- LETTERA -- */

const LETTERA_INPS = {
  mittente: "INPS — Direzione Provinciale di Milano",
  data: "22 settembre 2026",
  protocollo: "INPS.0920.22/09/2026.0034517",
  oggetto: "Comunicazione di accertamento di indebito pensionistico — verifica reddituale anno 2025",
  paragrafi: [
    {
      id: "P1",
      testo: "Gentile Sig. FERRETTI MARIO, titolare della pensione n. IT2340012345678, con la presente si comunica l'esito della verifica delle dichiarazioni reddituali di cui all'art. 13 della legge 30 dicembre 1991, n. 412 e successive modificazioni."
    },
    {
      id: "P2",
      testo: "Dalla predetta verifica è emerso che, per l'annualità 2025, le prestazioni collegate al reddito sono state corrisposte in misura superiore a quella spettante. L'importo complessivamente non dovuto ammonta a euro 340,00."
    },
    {
      id: "P3",
      testo: "Si procederà pertanto al recupero della somma sopra indicata mediante trattenuta sulle rate di pensione in corso di corresponsione, in misura non superiore a un quinto dell'importo mensile, a decorrere dalla mensilità di gennaio 2027."
    },
    {
      id: "P4",
      testo: "Qualora l'interessato intenda provvedere al versamento in unica soluzione, potrà utilizzare l'avviso di pagamento pagoPA disponibile nell'area riservata del portale istituzionale, previa autenticazione tramite SPID, CIE o CNS."
    },
    {
      id: "P5",
      testo: "Avverso il presente provvedimento è ammesso ricorso amministrativo al Comitato Provinciale dell'INPS entro il termine di novanta giorni dalla data di ricezione della presente comunicazione, ai sensi dell'art. 46 della legge 9 marzo 1989, n. 88."
    }
  ]
};

/* ------------------------------------------------------------- CONTATTI -- */

const CONTATTI = {
  inps_numero_verde: "803 164",
  inps_numero_verde_nota: "gratuito da rete fissa",
  inps_da_cellulare: "06 164 164",
  cup_lombardia: "800 638 638",
  sede_inps_milano: "Via Melchiorre Gioia 22, Milano — dal lunedì al venerdì, 8:30-12:30"
};

/* --------------------------------------------------------------- LIMITI -- */

const LIMITI = [
  "Le prenotazioni di questo prototipo sono simulate su dati di esempio: non arrivano al CUP reale.",
  "VoceAmica non dà diagnosi, consigli su farmaci, consulenza legale o fiscale.",
  "Spiega cosa dice un documento, non cosa conviene fare: per le decisioni servono lo sportello o il medico.",
  "La scheda di memoria resta salvata solo in questo browser, su questo computer. Si può leggere e cancellare in ogni momento.",
  "Funziona su Chrome ed Edge e richiede una connessione a internet."
];

/* ----------------------------------------------------------------- TOOL -- */

const TOOL_CONFERMA_PRENOTAZIONE = {
  name: "conferma_prenotazione",
  description:
    "Conferma definitivamente uno degli slot CUP disponibili per Mario. " +
    "Va chiamata SOLO dopo che Mario ha scelto esplicitamente uno slot. " +
    "Restituisce il codice di prenotazione da comunicare a Mario.",
  input_schema: {
    type: "object",
    properties: {
      slot_id: {
        type: "string",
        // Generato dagli slot esistenti: un enum più largo permetterebbe al modello
        // di scegliere uno slot che non c'è.
        enum: CUP_SLOTS.map(function (s) { return s.id; }),
        description: "Identificativo dello slot scelto da Mario."
      }
    },
    required: ["slot_id"],
    additionalProperties: false
  }
};

/* -------------------------------------------------------- SYSTEM PROMPT -- */

/* Il codice di prenotazione lo genera il codice, non il modello: è un dato verificato
 * e va nel blocco <DATI_VERIFICATI>, non nella memoria narrativa. Altrimenti alla
 * seconda chiamata la regola anti-invenzione lo renderebbe impronunciabile. */
const PREFISSO_PRENOTAZIONE = "CUP-2026-";

function datiVerificati(prenotazioni) {
  const slot = CUP_SLOTS.map(function (s) {
    return [
      "- " + s.id + ": " + s.prestazione,
      "  quando: " + s.data + " alle " + s.ora,
      "  dove: " + s.struttura + ", " + s.reparto + " — " + s.indirizzo,
      "  codice prestazione: " + s.codice_prestazione + " | priorità: " + s.classe_priorita,
      "  ticket: " + s.ticket,
      "  da portare: " + s.cosa_portare.join(", ")
    ].join("\n");
  }).join("\n");

  const lettera = LETTERA_INPS.paragrafi.map(function (p) {
    return "[" + p.id + "] " + p.testo;
  }).join("\n\n");

  const confermate = (prenotazioni && prenotazioni.length)
    ? [
        "",
        "PRENOTAZIONI GIÀ CONFERMATE PER MARIO (dati verificati dal sistema:",
        "puoi ripeterli, anche il codice)",
        prenotazioni.map(function (p) {
          return "- " + p.codice + ": " + p.prestazione + ", " + p.data + " alle " + p.ora +
                 ", " + p.struttura + " (" + p.indirizzo + "). Ticket " + p.ticket +
                 ". Da portare: " + p.cosa_portare.join(", ") + ".";
        }).join("\n")
      ].join("\n")
    : "";

  return [
    "SLOT CUP CHE CONOSCI (gli unici che puoi proporre: per altri giorni o orari di' che non hai quel dato e rimanda al CUP)",
    slot,
    confermate,
    "",
    "LETTERA RICEVUTA DA MARIO",
    "Mittente: " + LETTERA_INPS.mittente,
    "Data: " + LETTERA_INPS.data + " — Protocollo: " + LETTERA_INPS.protocollo,
    "Oggetto: " + LETTERA_INPS.oggetto,
    "",
    lettera,
    "",
    "CONTATTI UTILI",
    "- INPS numero verde: " + CONTATTI.inps_numero_verde + " (" + CONTATTI.inps_numero_verde_nota + ")",
    "- INPS da cellulare: " + CONTATTI.inps_da_cellulare,
    "- CUP Lombardia: " + CONTATTI.cup_lombardia,
    "- Sede INPS Milano: " + CONTATTI.sede_inps_milano
  ].join("\n");
}

/* La scheda di memoria, se esiste, entra nel prompt come contesto aggiuntivo:
 * è ciò che permette a VoceAmica di non far ripetere a Mario quello che ha già detto. */
function buildSystemPrompt(memoria, prenotazioni) {
  const bloccoMemoria = memoria
    ? [
        "",
        "<MEMORIA>",
        "Questa è la scheda delle chiamate precedenti con Mario. Usala per non fargli",
        "ripetere cose che ha già detto e per riprendere le pratiche lasciate in sospeso.",
        "Non trattarla come fonte di dati verificati: date, importi e codici validi sono",
        "solo quelli in <DATI_VERIFICATI>.",
        "",
        memoria,
        "</MEMORIA>"
      ].join("\n")
    : "";

  return [
    "Sei VoceAmica, un assistente vocale per Mario Ferretti, 72 anni.",
    "Parli con Mario esattamente come farebbe un figlio paziente e competente al telefono.",
    "",
    "REGOLE DI COMUNICAZIONE:",
    "- Frasi corte. Mai più di 2 frasi consecutive.",
    "- Zero termini burocratici: se devi usarne uno, spiegalo subito dopo.",
    '- Tono caldo, mai condiscendente. Mai "lei" — usa sempre "tu".',
    "- Proponi sempre UN SOLO passo successivo alla volta.",
    "- Se non capisci qualcosa, chiedi di ripetere in modo gentile.",
    "",
    "REGOLE SUI DATI — le più importanti, non derogabili:",
    "1. Usa ESCLUSIVAMENTE i dati in PROFILO MARIO e nel blocco <DATI_VERIFICATI>. Non inventare mai",
    "   date, orari, indirizzi, importi, numeri di telefono o codici. Se un dato",
    "   non c'è, di' che non lo sai e che bisogna chiederlo allo sportello.",
    "   Vale anche per <MEMORIA>: non pronunciare mai una data, un importo o un codice",
    "   che compare solo lì. La memoria serve a ricordare di cosa avete parlato, non a",
    "   stabilire fatti. Se ti serve un dato che è solo in memoria, rimanda allo sportello.",
    "2. Quando spieghi la lettera, chiudi la frase col marcatore del paragrafo da",
    "   cui prendi l'informazione, così: [P3]. Importi, date e scadenze vanno",
    "   ripetuti letteralmente come sono scritti, mai parafrasati o arrotondati.",
    "3. Per prenotare DEVI chiamare la funzione conferma_prenotazione. Non dire mai",
    '   "ho prenotato" prima di averne ricevuto il risultato.',
    "",
    "PROFILO MARIO:",
    JSON.stringify(MARIO, null, 2),
    "",
    "<DATI_VERIFICATI>",
    datiVerificati(prenotazioni),
    "</DATI_VERIFICATI>",
    bloccoMemoria,
    "",
    "COSA PUOI FARE:",
    "- Proporre e confermare una visita fra gli slot CUP disponibili",
    "- Spiegare in parole semplici la lettera che Mario ha ricevuto",
    "- Dire a chi rivolgersi usando i contatti verificati",
    "",
    "NON fare mai:",
    "- Diagnosi mediche",
    "- Consigli su farmaci",
    "- Consulenza legale o fiscale: spiega cosa dice il documento, non cosa conviene fare",
    "- Promesse su tempi o esiti reali"
  ].join("\n");
}

/* ----------------------------------------------------------- ARCHIVISTA -- */

/* Secondo ruolo, separato dalla conversazione: a chiamata chiusa riscrive la scheda
 * della persona. Non parla con Mario e non ha strumenti: produce solo markdown. */
function buildPromptArchivista() {
  return [
    "Sei l'archivista di VoceAmica. A chiamata conclusa aggiorni la scheda della persona",
    "che ha chiamato, perché alla prossima telefonata non debba ripetere quello che ha",
    "già detto.",
    "",
    "Produci SOLO un documento markdown, senza premesse né commenti, con questa struttura",
    "(ometti una sezione se non hai nulla da scriverci):",
    "",
    "# Nome della persona",
    "## Chi è",
    "## Dove si blocca",
    "## Pratiche concluse",
    "## In sospeso",
    "## Note per la prossima chiamata",
    "",
    "REGOLE, non derogabili:",
    "- Scrivi solo ciò che risulta dalla chiamata o dalla scheda precedente. Non aggiungere",
    "  nulla di inferito, nulla di plausibile, nulla di inventato.",
    "- Riporta date, importi e codici esattamente come compaiono: mai riscritti, mai arrotondati.",
    "- Non annotare valutazioni mediche, diagnosi o giudizi sulla persona. Registri fatti e",
    "  pratiche, non opinioni.",
    "- Se la scheda precedente conteneva una pratica che in questa chiamata si è conclusa,",
    "  spostala da «In sospeso» a «Pratiche concluse».",
    "- Frasi brevi. La scheda la può rileggere un familiare o un operatore allo sportello:",
    "  deve essere comprensibile senza conoscere il sistema.",
    "- Non riportare numeri di documento, codici fiscali o chiavi di accesso."
  ].join("\n");
}

function buildRichiestaArchivista(schedaPrecedente, battute, prenotazione, paragrafi) {
  const parti = [];

  parti.push("SCHEDA PRECEDENTE");
  parti.push(schedaPrecedente || "(nessuna: è la prima chiamata)");
  parti.push("");
  parti.push("TRASCRIZIONE DELLA CHIAMATA APPENA CONCLUSA");
  parti.push(
    battute.length
      ? battute.map(function (b) {
          return (b.chi === "mario" ? "Mario: " : "VoceAmica: ") + b.testo;
        }).join("\n")
      : "(nessuna battuta)"
  );
  parti.push("");
  parti.push("FATTI VERIFICATI DI QUESTA CHIAMATA");
  if (prenotazione) {
    parti.push(
      "- Prenotazione confermata dal sistema: " + prenotazione.prestazione + ", " +
      prenotazione.data + " alle " + prenotazione.ora + ", " + prenotazione.struttura +
      " (" + prenotazione.indirizzo + "). Codice " + prenotazione.codice +
      ". Ticket " + prenotazione.ticket + ". Da portare: " +
      prenotazione.cosa_portare.join(", ") + "."
    );
  }
  if (paragrafi && paragrafi.length) {
    parti.push(
      "- Spiegati i paragrafi " + paragrafi.join(", ") + " della comunicazione " +
      LETTERA_INPS.mittente + " del " + LETTERA_INPS.data + "."
    );
  }
  if (!prenotazione && !(paragrafi && paragrafi.length)) {
    parti.push("- Nessuna pratica conclusa.");
  }
  parti.push("");
  parti.push("Riscrivi la scheda aggiornata.");

  return parti.join("\n");
}
