/* VoceAmica — CALL ENGINE + GROUNDED LLM + EVIDENZA
 * Dipende da data.js, che deve essere caricato prima.
 */

const MODEL = "claude-haiku-4-5";
const MAX_TOKENS = 700;
const API_URL = "https://api.anthropic.com/v1/messages";
const SALUTO = "Ciao Mario! Sono VoceAmica. Come posso aiutarti oggi?";

/* Parametri della voce. Con la pausa fra le frasi il ritmo può stare quasi a velocità
 * naturale: la lentezza che serve a Mario la danno i respiri, non il rallentamento,
 * che invece fa suonare la voce artificiale. Da ritoccare ascoltando, non ragionando. */
const RITMO_VOCE = 0.95;
const PAUSA_FRA_FRASI = 350;

/* Chiave di memoria per persona: il giorno in cui chiamerà anche Teresa, cambia solo
 * il profilo caricato, non il meccanismo. */
const SLUG_PERSONA = MARIO.nome.toLowerCase().replace(/\s+/g, "-");
const CHIAVE_SCHEDA = "voceamica:scheda:" + SLUG_PERSONA;
const CHIAVE_PRENOTAZIONI = "voceamica:prenotazioni:" + SLUG_PERSONA;

let systemPrompt = buildSystemPrompt(caricaScheda(), caricaPrenotazioni());

const STATO = {
  IDLE: "IDLE",
  LISTENING: "LISTENING",
  PROCESSING: "PROCESSING",
  SPEAKING: "SPEAKING",
  ENDED: "ENDED"
};

let stato = STATO.IDLE;
let history = [];
let apiKey = "";
let recognition = null;
let isSpeaking = false;
let silenzioTimer = null;
let silenzioGiaChiesto = false;
let sessione = { prenotazione: null, paragrafi: [], primaRichiesta: "", battute: [] };

const $ = function (id) { return document.getElementById(id); };

/* ============================================================ BOOTSTRAP == */

/* Aperta con un doppio clic (file://), Chrome non ricorda il permesso del microfono
 * e lo richiede a ogni turno, perché ogni turno apre un microfono nuovo. */
const APERTA_DA_FILE = location.protocol === "file:";
const AVVISO_FILE = "Apri VoceAmica da http://localhost:8000/app/ e non con un doppio clic: " +
                    "così Chrome chiede il permesso del microfono una volta sola.";

function init() {
  renderMario();
  renderLimiti();
  renderLettera($("lettera-prima"));
  renderLettera($("lettera-live"));

  $("tab-prima").addEventListener("click", function () { mostraTab("prima"); });
  $("tab-voce").addEventListener("click", function () { mostraTab("voce"); });
  $("btn-chiama").addEventListener("click", avviaChiamata);
  $("btn-riaggancia").addEventListener("click", riaggancia);
  $("btn-nuova").addEventListener("click", nuovaChiamata);
  $("demo-a").addEventListener("click", function () {
    quickLaunch("Vorrei prenotare una visita cardiologica, ma non so come fare");
  });
  $("demo-b").addEventListener("click", function () {
    quickLaunch("Mi è arrivata una lettera dall'INPS, non capisco cosa vogliono. Parla di una somma da restituire");
  });
  $("btn-invia").addEventListener("click", inviaTesto);
  $("btn-scarica-scheda").addEventListener("click", scaricaScheda);
  $("btn-dimentica-scheda").addEventListener("click", dimenticaScheda);
  $("input-testo").addEventListener("keydown", function (e) {
    if (e.key === "Enter") inviaTesto();
  });
  $("api-key").addEventListener("input", function (e) { apiKey = e.target.value.trim(); });

  if (!supportaRiconoscimento()) {
    $("fallback").classList.add("attivo");
    avvisa("Questo browser non riconosce la voce: usa Chrome o Edge, oppure scrivi nel campo qui sotto.");
  }
  setStato(STATO.IDLE);
  if (APERTA_DA_FILE) avvisa(AVVISO_FILE);
}

function renderMario() {
  $("m-nome").textContent = MARIO.nome;
  $("m-eta").textContent = MARIO.eta + " anni · " + MARIO.citta;
  $("m-barriera").textContent = MARIO.barriera;
  $("m-medico").textContent = MARIO.medico_base;
  $("m-tel").textContent = MARIO.telefono;
  $("m-farmaci").textContent = MARIO.farmaci.join(", ");
  $("m-tessera").textContent = "scade il " + formattaData(MARIO.documenti_importanti.tessera_sanitaria_scadenza);

  const ul = $("m-storico");
  MARIO.storico_interazioni.forEach(function (s) {
    const li = document.createElement("li");
    li.textContent = s.descrizione;
    ul.appendChild(li);
  });
}

function renderLimiti() {
  const ul = $("lista-limiti");
  LIMITI.forEach(function (t) {
    const li = document.createElement("li");
    li.textContent = t;
    ul.appendChild(li);
  });
}

function renderLettera(contenitore) {
  contenitore.innerHTML = "";

  const head = document.createElement("div");
  head.className = "lettera-head";
  const mitt = document.createElement("div");
  mitt.className = "mitt";
  mitt.textContent = LETTERA_INPS.mittente;
  const meta = document.createElement("div");
  meta.textContent = LETTERA_INPS.data + " — Prot. " + LETTERA_INPS.protocollo;
  head.appendChild(mitt);
  head.appendChild(meta);
  contenitore.appendChild(head);

  const ogg = document.createElement("div");
  ogg.className = "lettera-ogg";
  ogg.textContent = "OGGETTO: " + LETTERA_INPS.oggetto;
  contenitore.appendChild(ogg);

  LETTERA_INPS.paragrafi.forEach(function (p) {
    const el = document.createElement("p");
    el.dataset.pid = p.id;
    el.textContent = p.testo;
    contenitore.appendChild(el);
  });
}

function formattaData(iso) {
  const parti = iso.split("-");
  return parti[2] + "/" + parti[1] + "/" + parti[0];
}

/* ================================================================= TAB === */

function mostraTab(quale) {
  const prima = quale === "prima";
  $("tab-prima").setAttribute("aria-selected", String(prima));
  $("tab-voce").setAttribute("aria-selected", String(!prima));
  $("vista-prima").classList.toggle("nascosto", !prima);
  $("vista-chiamata").classList.toggle("nascosto", prima || stato === STATO.ENDED);
  $("vista-riepilogo").classList.toggle("attivo", !prima && stato === STATO.ENDED);
}

/* ====================================================== STATI VISIVI ===== */

function setStato(nuovo) {
  stato = nuovo;
  const cerchio = $("cerchio");
  const testo = $("stato-testo");
  cerchio.className = "cerchio";

  if (nuovo === STATO.IDLE) {
    cerchio.textContent = "📞";
    testo.textContent = "Premi il pulsante verde per chiamare VoceAmica";
    $("btn-chiama").classList.remove("nascosto");
    $("btn-riaggancia").classList.add("nascosto");
    $("demo-row").classList.add("nascosto");
    $("parlato").textContent = "";
    $("risposta").textContent = "";
  } else if (nuovo === STATO.LISTENING) {
    cerchio.textContent = "🎤";
    cerchio.classList.add("pulse-blu");
    // A Mario si dà del tu, e gli si dice cosa fare: il microfono aspetta lui.
    testo.textContent = "Ti ascolto: parla pure.";
  } else if (nuovo === STATO.PROCESSING) {
    cerchio.textContent = "⏳";
    testo.textContent = "Sto cercando…";
    $("parlato").textContent = "";
  } else if (nuovo === STATO.SPEAKING) {
    cerchio.textContent = "🔊";
    cerchio.classList.add("pulse-verde");
    testo.textContent = "VoceAmica sta rispondendo…";
  }

  if (nuovo !== STATO.LISTENING) fermaTimerSilenzio();
}

function avvisa(messaggio) {
  const box = $("avviso");
  box.textContent = messaggio;
  box.classList.add("attivo");
}

function nascondiAvviso() {
  $("avviso").classList.remove("attivo");
}

/* ======================================================== CICLO CHIAMATA = */

async function avviaChiamata() {
  apiKey = $("api-key").value.trim();
  if (!apiKey) {
    avvisa("Inserisci la chiave API per iniziare: la trovi in «Accesso», nella colonna a sinistra.");
    return;
  }
  if (APERTA_DA_FILE) avvisa(AVVISO_FILE); else nascondiAvviso();
  mostraTab("voce");

  history = [];
  sessione = { prenotazione: null, paragrafi: [], primaRichiesta: "", battute: [] };
  // La scheda delle chiamate precedenti entra nel prompt di questa chiamata.
  systemPrompt = buildSystemPrompt(caricaScheda(), caricaPrenotazioni());
  silenzioGiaChiesto = false;
  $("bolle").innerHTML = "";
  $("esito").classList.remove("attivo");
  $("card-lettera-live").classList.add("nascosto");
  $("vista-riepilogo").classList.remove("attivo");
  $("vista-chiamata").classList.remove("nascosto");
  pulisciEvidenziazioni();

  $("btn-chiama").classList.add("nascosto");
  $("btn-riaggancia").classList.remove("nascosto");
  $("demo-row").classList.remove("nascosto");
  // Canale di scorta sempre aperto durante la chiamata: se il microfono cede a
  // metà flusso, i pulsanti demo coprono solo la prima battuta.
  $("fallback").classList.add("attivo");

  setStato(STATO.SPEAKING);
  $("risposta").textContent = SALUTO;
  aggiungiBolla("voce", SALUTO, null);
  await parla(SALUTO);
  tornaInAscolto();
}

function tornaInAscolto() {
  if (stato === STATO.ENDED) return;
  setStato(STATO.LISTENING);
  setTimeout(function () {
    if (stato === STATO.LISTENING) {
      avviaAscolto();
      avviaTimerSilenzio();
    }
  }, 300);
}

async function gestisciTurno(testoUtente) {
  if (!testoUtente || stato === STATO.ENDED) return;
  // Un turno per volta. Due turni sovrapposti scriverebbero sulla stessa history
  // e la richiesta successiva partirebbe malformata.
  if (stato === STATO.PROCESSING || stato === STATO.SPEAKING) {
    avvisa("Un momento: VoceAmica sta ancora rispondendo. Riprova appena ha finito.");
    return;
  }

  fermaAscolto();
  fermaTimerSilenzio();
  if (!sessione.primaRichiesta) sessione.primaRichiesta = testoUtente;
  aggiungiBolla("mario", testoUtente, null);
  setStato(STATO.PROCESSING);

  let esito;
  // Se il turno fallisce la history torna come prima: un messaggio di Mario
  // rimasto senza risposta renderebbe malformato anche il turno successivo.
  const historyPrima = history.slice();
  try {
    esito = await askClaude(testoUtente);
  } catch (errore) {
    history = historyPrima;
    console.error(errore);   // il dettaglio tecnico resta in console, per noi
    // Riagganciato mentre la richiesta era in volo: niente scuse a voce e niente
    // microfono riaperto a chiamata chiusa.
    if (stato === STATO.ENDED) return;
    const scusa = "Scusa Mario, ho avuto un problema. Riprova tra un momento.";
    avvisa("Non riesco a collegarmi in questo momento. Riprova, oppure scrivi nel campo qui sotto.");
    setStato(STATO.SPEAKING);
    $("risposta").textContent = scusa;
    aggiungiBolla("voce", scusa, null);
    await parla(scusa);
    tornaInAscolto();
    return;
  }

  if (stato === STATO.ENDED) return;

  nascondiAvviso();   // il turno è andato: via l'avviso rosso del tentativo precedente
  setStato(STATO.SPEAKING);
  $("risposta").textContent = esito.testoPulito;
  aggiungiBolla("voce", esito.testoPulito, provenienza(esito));

  if (esito.paragrafi.length) {
    $("card-lettera-live").classList.remove("nascosto");
    evidenziaParagrafi(esito.paragrafi);
    esito.paragrafi.forEach(function (p) {
      if (sessione.paragrafi.indexOf(p) === -1) sessione.paragrafi.push(p);
    });
  }

  await parla(esito.testoPulito);
  tornaInAscolto();
}

function quickLaunch(testo) {
  if (stato === STATO.IDLE || stato === STATO.ENDED) {
    avvisa("Avvia prima la chiamata, poi usa i pulsanti della demo.");
    return;
  }
  $("parlato").textContent = testo;
  gestisciTurno(testo);
}

function inviaTesto() {
  const campo = $("input-testo");
  const testo = campo.value.trim();
  if (!testo) return;
  if (stato === STATO.IDLE || stato === STATO.ENDED) {
    avvisa("Avvia prima la chiamata con il pulsante verde.");
    return;
  }
  campo.value = "";
  gestisciTurno(testo);
}

function riaggancia() {
  stato = STATO.ENDED;
  fermaAscolto();
  // Prima la guardia della sintesi, poi la sintesi: se cancel() non emette onend
  // (il caso per cui la guardia esiste) il timer resterebbe armato e cancellerebbe
  // la voce della chiamata successiva.
  if (chiudiParlato) chiudiParlato();
  if (window.speechSynthesis) window.speechSynthesis.cancel();
  isSpeaking = false;
  fermaTimerSilenzio();
  $("btn-riaggancia").classList.add("nascosto");
  $("demo-row").classList.add("nascosto");
  $("fallback").classList.remove("attivo");
  renderRiepilogo();
  $("vista-chiamata").classList.add("nascosto");
  $("vista-riepilogo").classList.add("attivo");
  // Il pulsante appena premuto è sparito: il focus va al titolo del riepilogo,
  // non resta perso in cima alla pagina.
  $("r-titolo").focus();
  aggiornaScheda();
}

function nuovaChiamata() {
  $("vista-riepilogo").classList.remove("attivo");
  $("vista-chiamata").classList.remove("nascosto");
  // La chiamata precedente non deve restare a schermo mentre siamo in attesa.
  $("bolle").innerHTML = "";
  $("esito").classList.remove("attivo");
  $("card-lettera-live").classList.add("nascosto");
  pulisciEvidenziazioni();
  if (!supportaRiconoscimento()) $("fallback").classList.add("attivo");
  setStato(STATO.IDLE);
  $("btn-chiama").focus();   // l'unico passo successivo, già sotto il dito
}

/* =========================================================== WEB SPEECH = */

function supportaRiconoscimento() {
  return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
}

function avviaAscolto() {
  if (!supportaRiconoscimento()) {
    $("fallback").classList.add("attivo");
    return;
  }
  const Classe = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new Classe();
  recognition.lang = "it-IT";
  recognition.continuous = false;      // single-shot: un turno per volta
  recognition.interimResults = true;

  recognition.onresult = function (evento) {
    // Difesa: scarta qualsiasi cattura fuori turno (eco della voce sintetica)
    if (isSpeaking || stato !== STATO.LISTENING) return;

    let parziale = "";
    let definitivo = "";
    for (let i = evento.resultIndex; i < evento.results.length; i++) {
      const frammento = evento.results[i][0].transcript;
      if (evento.results[i].isFinal) definitivo += frammento;
      else parziale += frammento;
    }
    $("parlato").textContent = definitivo || parziale;
    if (definitivo.trim()) {
      fermaTimerSilenzio();
      gestisciTurno(definitivo.trim());
    } else if (parziale.trim()) {
      // Mario sta ancora parlando: il silenzio si conta dall'ultima parola.
      avviaTimerSilenzio();
    }
  };

  recognition.onerror = function (evento) {
    // no-speech e aborted sono normali: decide onend se riaprire il microfono.
    if (evento.error === "no-speech" || evento.error === "aborted") return;
    // Per ogni altro errore il microfono non riparte da solo: se non lo spengo,
    // onend lo riavvia subito e l'errore si ripete in loop.
    fermaAscolto();
    $("fallback").classList.add("attivo");
    $("stato-testo").textContent = "Scrivi qui sotto cosa vuoi dire";
    if (evento.error === "not-allowed" || evento.error === "service-not-allowed") {
      avvisa("Non ho il permesso di usare il microfono. Puoi scrivere nel campo qui sotto.");
    } else {
      avvisa("Il microfono non funziona in questo momento. Puoi scrivere nel campo qui sotto.");
    }
  };

  recognition.onend = function () {
    // Riapri il microfono solo se siamo ancora nel turno di Mario
    if (stato === STATO.LISTENING && !isSpeaking) {
      try { recognition.start(); } catch (e) { /* già attivo */ }
    }
  };

  try { recognition.start(); } catch (e) { /* già attivo */ }
}

function fermaAscolto() {
  if (recognition) {
    recognition.onend = null;
    recognition.onresult = null;
    try { recognition.abort(); } catch (e) { /* ignora */ }
    recognition = null;
  }
}

/* Riferimento alla chiusura del parlato in corso: chi riaggancia deve poter
 * spegnere la guardia, altrimenti scatta dentro la chiamata successiva e ne
 * cancella la voce. */
let chiudiParlato = null;

function parla(testo) {
  return new Promise(function (resolve) {
    fermaAscolto();                     // il microfono non esiste mentre si parla
    const frasi = spezzaInFrasi(perLaVoce(testo || ""));
    if (!window.speechSynthesis || !frasi.length) { resolve(); return; }

    isSpeaking = true;
    let indice = 0;
    let chiuso = false;
    let guardia = null;

    const fine = function () {
      if (chiuso) return;
      chiuso = true;
      if (guardia) clearTimeout(guardia);
      if (chiudiParlato === fine) chiudiParlato = null;
      isSpeaking = false;
      resolve();
    };
    chiudiParlato = fine;

    const diLaProssima = function () {
      if (chiuso) return;
      if (indice >= frasi.length) { fine(); return; }

      const frase = frasi[indice++];
      const u = new SpeechSynthesisUtterance(frase);
      u.lang = "it-IT";
      u.rate = RITMO_VOCE;
      u.pitch = 1.0;
      const voce = vocePreferita();
      if (voce) u.voice = voce;

      let passata = false;
      const avanti = function () {
        if (passata || chiuso) return;
        passata = true;
        if (guardia) clearTimeout(guardia);
        setTimeout(diLaProssima, PAUSA_FRA_FRASI);
      };
      u.onend = avanti;
      u.onerror = function () {
        // Voce di rete caduta: una sola volta si riprova la stessa frase con una
        // voce locale, invece di proseguire in silenzio.
        if (!voceDiReteFallita && voce && voce.localService === false && !passata && !chiuso) {
          voceDiReteFallita = true;
          indice--;
          if (guardia) clearTimeout(guardia);
          setTimeout(diLaProssima, 100);
          return;
        }
        avanti();
      };

      // Chrome a volte non emette né onend né onerror: senza questa guardia la
      // chiamata resterebbe bloccata in SPEAKING e la demo morirebbe lì.
      guardia = setTimeout(function () {
        if (chiuso || passata) return;
        try { window.speechSynthesis.cancel(); } catch (e) { /* ignora */ }
        avanti();
      }, 2500 + frase.length * 120);

      window.speechSynthesis.speak(u);
    };

    diLaProssima();
  });
}

/* Le voci su Chrome arrivano in modo asincrono: al primo saluto getVoices() può
 * essere ancora vuoto, e Mario si sentirebbe rispondere con accento inglese. */
let vociInMemoria = [];

function caricaVoci() {
  if (!window.speechSynthesis) return;
  const v = window.speechSynthesis.getVoices();
  if (v && v.length) vociInMemoria = v;
}

function vociItaliane() {
  if (!vociInMemoria.length) caricaVoci();
  return vociInMemoria.filter(function (v) {
    return v.lang && v.lang.toLowerCase().indexOf("it") === 0;
  });
}

/* Non tutte le voci italiane suonano uguali: prendere la prima della lista significa
 * di solito prendere una voce SAPI di sistema, la più metallica. Le voci di rete di
 * Google e le "Natural" di Edge sono di un'altra generazione. */
/* Le voci migliori sono spesso voci di rete: se la connessione cade restano mute,
 * e VoceAmica senza voce non è più niente. Al primo errore si ripiega sul locale. */
let voceDiReteFallita = false;

function vocePreferita() {
  const italiane = vociItaliane();
  if (!italiane.length) return null;

  if (voceDiReteFallita) {
    const locali = italiane.filter(function (v) { return v.localService; });
    if (locali.length) return locali[0];
  }

  const punteggio = function (v) {
    const nome = (v.name || "").toLowerCase();
    let p = 0;
    if (nome.indexOf("natural") !== -1) p += 100;   // voci neurali (Edge)
    if (nome.indexOf("google") !== -1) p += 90;     // voce di rete di Chrome
    if (v.localService === false) p += 20;          // le voci di rete suonano meglio
    if (v.lang && v.lang.toLowerCase() === "it-it") p += 5;
    return p;
  };

  return italiane.slice().sort(function (a, b) {
    return punteggio(b) - punteggio(a);
  })[0];
}

/* Il sintetizzatore legge i numeri e le abbreviazioni come sono scritti, non come si
 * dicono: "09:30" diventa "zero nove due punti tre zero". Qui si scrive per l'orecchio. */
/* Il modello a volte scrive [P2, P3] o [P2-P3] invece di [P2] [P3]: vanno accettate
 * tutte, altrimenti il marcatore finisce letto ad alta voce. */
const MARCATORE = /\s*\[P\d+(?:\s*[,\-–]\s*P?\d+)*\]/g;

function perLaVoce(testo) {
  return testo
    .replace(MARCATORE, "")
    .replace(/[*_`#]/g, "")
    .replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu, "")
    .replace(/euro\s+(\d+),(\d{2})/gi, function (_, interi, cent) {
      return cent === "00" ? interi + " euro" : interi + " euro e " + cent;
    })
    .replace(/(\d+),(\d{2})\s*euro/gi, function (_, interi, cent) {
      return cent === "00" ? interi + " euro" : interi + " euro e " + cent;
    })
    .replace(/\b0?(\d{1,2}):(\d{2})\b/g, function (_, ore, minuti) {
      return minuti === "00" ? ore : ore + " e " + minuti;
    })
    .replace(/\b([A-Z]{2,})-(\d{4})-(\d{3,4})\b/g, "$1 $2 $3")
    .replace(/\bdott\.ssa\b/gi, "dottoressa")
    .replace(/\bdott\./gi, "dottor")
    .replace(/\bSig\.ra\b/g, "signora")
    .replace(/\bSig\./g, "signor")
    .replace(/\bn\.\s*(?=\d)/g, "numero ")
    .replace(/\bart\.\s*(?=\d)/g, "articolo ")
    .replace(/\becc\./gi, "eccetera")
    .replace(/\s{2,}/g, " ")
    .trim();
}

/* Una sola utterance lunga esce piatta, senza respiro. Spezzare per frasi e lasciare
 * una pausa fra l'una e l'altra è ciò che fa somigliare la voce a una persona —
 * e per Mario è anche più facile da seguire. */
function spezzaInFrasi(testo) {
  const pezzi = testo.match(/[^.!?…]+[.!?…]*/g);
  if (!pezzi) return testo ? [testo] : [];

  const frasi = [];
  pezzi.forEach(function (pezzo) {
    const f = pezzo.trim();
    if (!f) return;
    // Frammenti troppo corti ("Sì.", "Perfetto.") si attaccano al precedente:
    // da soli suonerebbero mozzati.
    if (frasi.length && f.length < 15) frasi[frasi.length - 1] += " " + f;
    else frasi.push(f);
  });

  // Un frammento corto in apertura non ha un precedente a cui attaccarsi:
  // si porta avanti il successivo, altrimenti resterebbe una parola isolata.
  if (frasi.length > 1 && frasi[0].length < 15) {
    frasi[1] = frasi[0] + " " + frasi[1];
    frasi.shift();
  }
  return frasi;
}

function avviaTimerSilenzio() {
  fermaTimerSilenzio();
  if (silenzioGiaChiesto) return;
  silenzioTimer = setTimeout(async function () {
    if (stato !== STATO.LISTENING) return;
    silenzioGiaChiesto = true;
    const sollecito = "Mario, sei ancora lì? Dimmi pure quando sei pronto.";
    setStato(STATO.SPEAKING);
    $("risposta").textContent = sollecito;
    await parla(sollecito);
    tornaInAscolto();
  }, 8000);
}

function fermaTimerSilenzio() {
  if (silenzioTimer) { clearTimeout(silenzioTimer); silenzioTimer = null; }
}

/* ======================================================= GROUNDED LLM === */

async function askClaude(testoUtente) {
  history.push({ role: "user", content: testoUtente });
  potaHistory();

  let usatoTool = false;

  for (let giro = 0; giro < 4; giro++) {
    const risposta = await chiamaApi({
      system: systemPrompt,
      messages: history,
      tools: [TOOL_CONFERMA_PRENOTAZIONE]
    });
    history.push({ role: "assistant", content: risposta.content });

    if (risposta.stop_reason === "tool_use") {
      // A chiamata chiusa non si prenota: il riepilogo è già stato mostrato senza.
      if (stato === STATO.ENDED) throw new Error("Chiamata chiusa durante il turno");
      const risultati = risposta.content
        .filter(function (b) { return b.type === "tool_use"; })
        .map(eseguiTool);
      history.push({ role: "user", content: risultati });
      // Il chip «confermata dal sistema» solo se il codice ha davvero confermato.
      if (risultati.some(function (r) { return !r.is_error; })) usatoTool = true;
      continue;
    }

    let testo = risposta.content
      .filter(function (b) { return b.type === "text"; })
      .map(function (b) { return b.text; })
      .join(" ")
      .trim();

    // Risposta tagliata dal tetto di token: meglio fermarsi all'ultima frase
    // compiuta che far sentire a Mario una parola spezzata a metà.
    if (risposta.stop_reason === "max_tokens") {
      // Il tetto può troncare anche il JSON di una chiamata a funzione: un blocco
      // tool_use senza tool_result resterebbe in history e farebbe fallire con 400
      // ogni turno successivo della chiamata. In history tengo solo il testo.
      history[history.length - 1].content = risposta.content.filter(function (b) {
        return b.type === "text";
      });

      const taglio = Math.max(testo.lastIndexOf("."), testo.lastIndexOf("?"), testo.lastIndexOf("!"));
      if (taglio > 40) testo = testo.slice(0, taglio + 1);
      // Nessun testo utilizzabile: meglio l'errore, che rimette a posto la history
      // e fa riprovare Mario, di una bolla vuota e del silenzio in sala.
      if (!testo.trim()) throw new Error("Risposta troncata senza testo utilizzabile");
    }

    // A volte, dopo il risultato della funzione, il modello chiude senza testo. Un
    // messaggio assistant vuoto in history farebbe fallire con 400 ogni turno dopo.
    if (!testo) {
      if (!usatoTool || !sessione.prenotazione) throw new Error("Risposta vuota");
      const p = sessione.prenotazione;
      testo = "Fatto, ho prenotato. Il tuo codice è " + p.codice + ". Ti aspettano " +
              p.data + " alle " + p.ora + ", " + p.struttura + ".";
      history[history.length - 1].content = [{ type: "text", text: testo }];
    }

    return {
      // Gli asterischi del markdown a voce si tolgono già; qui spariscono anche dalle bolle.
      testoPulito: testo.replace(MARCATORE, "").replace(/\*\*|__/g, "").trim(),
      paragrafi: estraiParagrafi(testo),
      usatoTool: usatoTool
    };
  }
  throw new Error("Troppi giri di chiamate a funzione");
}

async function chiamaApi(opzioni) {
  const corpo = {
    model: MODEL,
    max_tokens: opzioni.maxTokens || MAX_TOKENS,
    system: opzioni.system,
    messages: opzioni.messages
  };
  if (opzioni.tools) corpo.tools = opzioni.tools;

  const risposta = await fetch(API_URL, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      // Senza questo header il browser blocca la richiesta in CORS.
      "anthropic-dangerous-direct-browser-access": "true"
    },
    body: JSON.stringify(corpo)
  });

  if (!risposta.ok) {
    const dettaglio = await risposta.text();
    throw new Error(risposta.status + " " + dettaglio.slice(0, 200));
  }
  return risposta.json();
}

/* Il modello sceglie lo slot, il codice lo conferma. */
function eseguiTool(blocco) {
  if (blocco.name !== "conferma_prenotazione") {
    return {
      type: "tool_result", tool_use_id: blocco.id, is_error: true,
      content: "Funzione non disponibile."
    };
  }

  const slot = CUP_SLOTS.filter(function (s) { return s.id === blocco.input.slot_id; })[0];
  if (!slot) {
    return {
      type: "tool_result", tool_use_id: blocco.id, is_error: true,
      content: "slot_id non valido. Gli slot disponibili sono " +
        CUP_SLOTS.map(function (s) { return s.id; }).join(", ") + "."
    };
  }

  const codice = PREFISSO_PRENOTAZIONE + Math.floor(1000 + Math.random() * 9000);
  sessione.prenotazione = Object.assign({ codice: codice }, slot);
  salvaPrenotazione(sessione.prenotazione);
  renderEsito();

  return {
    type: "tool_result",
    tool_use_id: blocco.id,
    content: JSON.stringify({
      esito: "confermata",
      codice_prenotazione: codice,
      quando: slot.data + " alle " + slot.ora,
      dove: slot.struttura + ", " + slot.reparto + ", " + slot.indirizzo,
      ticket: slot.ticket,
      cosa_portare: slot.cosa_portare
    })
  };
}

function estraiParagrafi(testo) {
  const trovati = [];
  (testo.match(MARCATORE) || []).forEach(function (m) {
    (m.match(/\d+/g) || []).forEach(function (n) { trovati.push("P" + n); });
  });
  const unici = [];
  trovati.forEach(function (id) {
    // Un marcatore di un paragrafo che non esiste non è un dato verificato.
    const esiste = LETTERA_INPS.paragrafi.some(function (p) { return p.id === id; });
    if (esiste && unici.indexOf(id) === -1) unici.push(id);
  });
  return unici;
}

/* Potatura sicura: non lascia mai un tool_result orfano in testa. */
function potaHistory() {
  const MAX = 16;
  while (history.length > MAX) {
    history.shift();
    while (history.length && !(history[0].role === "user" && typeof history[0].content === "string")) {
      history.shift();
    }
  }
}

/* ============================================================ EVIDENZA == */

function provenienza(esito) {
  if (esito.usatoTool) {
    return { tipo: "verificato", testo: "Dato verificato — prenotazione CUP confermata dal sistema" };
  }
  if (esito.paragrafi.length) {
    const numeri = esito.paragrafi.map(function (p) { return p.replace("P", ""); }).join(", ");
    const plurale = esito.paragrafi.length > 1 ? "paragrafi" : "paragrafo";
    return { tipo: "verificato", testo: "Dato verificato — lettera INPS, " + plurale + " " + numeri };
  }
  return { tipo: "generato", testo: "Spiegazione generata dall'AI — da confermare allo sportello" };
}

function aggiungiBolla(ruolo, testo, prov) {
  sessione.battute.push({ chi: ruolo, testo: testo });

  const bolla = document.createElement("div");
  bolla.className = "bolla " + ruolo;

  const corpo = document.createElement("div");
  corpo.className = "testo";
  corpo.textContent = testo;
  bolla.appendChild(corpo);

  if (prov) {
    const chip = document.createElement("span");
    chip.className = "chip " + prov.tipo;
    chip.textContent = (prov.tipo === "verificato" ? "✓ " : "• ") + prov.testo;
    bolla.appendChild(chip);
  }

  const contenitore = $("bolle");
  contenitore.appendChild(bolla);
  contenitore.scrollTop = contenitore.scrollHeight;
}

function evidenziaParagrafi(ids) {
  pulisciEvidenziazioni();
  ["lettera-live", "lettera-prima"].forEach(function (contenitore) {
    ids.forEach(function (id) {
      const p = $(contenitore).querySelector('[data-pid="' + id + '"]');
      if (p) p.classList.add("evidenziato");
    });
  });
  const primo = $("lettera-live").querySelector(".evidenziato");
  if (primo) primo.scrollIntoView({ behavior: "smooth", block: "center" });
}

function pulisciEvidenziazioni() {
  document.querySelectorAll(".lettera p.evidenziato").forEach(function (p) {
    p.classList.remove("evidenziato");
  });
}

function renderEsito() {
  const p = sessione.prenotazione;
  if (!p) return;
  const box = $("esito");
  box.innerHTML = "";

  const h3 = document.createElement("h3");
  h3.textContent = "✓ Visita prenotata";
  box.appendChild(h3);

  const codice = document.createElement("div");
  codice.className = "codice";
  codice.textContent = p.codice;
  box.appendChild(codice);

  const quando = document.createElement("div");
  quando.textContent = p.data + " alle " + p.ora + " — " + p.struttura;
  box.appendChild(quando);

  const dove = document.createElement("div");
  dove.textContent = p.reparto + ", " + p.indirizzo;
  box.appendChild(dove);

  const ticket = document.createElement("div");
  ticket.textContent = "Ticket: " + p.ticket;
  box.appendChild(ticket);

  const titolo = document.createElement("div");
  titolo.style.marginTop = "12px";
  titolo.innerHTML = "<strong>Cosa portare</strong>";
  box.appendChild(titolo);

  const ul = document.createElement("ul");
  p.cosa_portare.forEach(function (c) {
    const li = document.createElement("li");
    li.textContent = c;
    ul.appendChild(li);
  });
  box.appendChild(ul);

  box.classList.add("attivo");
}

function renderRiepilogo() {
  $("r-chiesto").textContent = sessione.primaRichiesta || "Nessuna richiesta in questa chiamata.";

  const fatto = $("r-fatto");
  fatto.innerHTML = "";
  const tuo = $("r-tuo");
  tuo.innerHTML = "";

  if (sessione.prenotazione) {
    const p = sessione.prenotazione;
    aggiungiRiga(fatto, "Visita prenotata: " + p.prestazione + ", " + p.data +
      " alle " + p.ora + " — " + p.struttura + ".");
    aggiungiRiga(fatto, "Codice di prenotazione: " + p.codice + ".");
    const ul = document.createElement("ul");
    p.cosa_portare.forEach(function (c) {
      const li = document.createElement("li");
      li.textContent = c;
      ul.appendChild(li);
    });
    aggiungiRiga(tuo, "Presentati il " + p.data + " alle " + p.ora + " a " + p.indirizzo +
      ", portando con te:");
    tuo.appendChild(ul);
    aggiungiRiga(tuo, "Il ticket da pagare è di " + p.ticket + ".");
  }

  if (sessione.paragrafi.length) {
    aggiungiRiga(fatto, "Spiegata la lettera dell'INPS del " + LETTERA_INPS.data +
      " (paragrafi " + sessione.paragrafi.map(function (x) { return x.replace("P", ""); }).join(", ") +
      "), senza modificare importi né scadenze.");
    aggiungiRiga(tuo, "Per conferma puoi chiamare il numero verde INPS " +
      CONTATTI.inps_numero_verde + ", " + CONTATTI.inps_numero_verde_nota + ".");
  }

  if (!fatto.children.length) {
    aggiungiRiga(fatto, "In questa chiamata non è stata completata nessuna pratica.");
  }
  if (!tuo.children.length) {
    aggiungiRiga(tuo, "Niente: per ora non c'è nulla in sospeso.");
  }

  const limiti = $("r-limiti");
  limiti.innerHTML = "";
  LIMITI.forEach(function (t) {
    const li = document.createElement("li");
    li.textContent = t;
    limiti.appendChild(li);
  });
}

function aggiungiRiga(contenitore, testo) {
  const p = document.createElement("p");
  p.textContent = testo;
  contenitore.appendChild(p);
}

/* ========================================================== ARCHIVISTA == */

function caricaPrenotazioni() {
  try {
    return JSON.parse(window.localStorage.getItem(CHIAVE_PRENOTAZIONI) || "[]");
  } catch (e) {
    return [];
  }
}

function salvaPrenotazione(prenotazione) {
  try {
    const tutte = caricaPrenotazioni();
    tutte.push(prenotazione);
    window.localStorage.setItem(CHIAVE_PRENOTAZIONI, JSON.stringify(tutte.slice(-5)));
  } catch (e) { /* senza storage si perde solo la memoria fra chiamate */ }
}

function caricaScheda() {
  try {
    return window.localStorage.getItem(CHIAVE_SCHEDA) || "";
  } catch (e) {
    return "";   // navigazione privata o storage negato: si procede senza memoria
  }
}

function salvaScheda(markdown) {
  try {
    window.localStorage.setItem(CHIAVE_SCHEDA, markdown);
    return true;
  } catch (e) {
    return false;
  }
}

/* «Cancella tutto» è irreversibile e sta accanto a «Scarica»: un tocco sbagliato
 * non deve bastare. Il primo tocco chiede conferma, il secondo cancella. */
const ETICHETTA_CANCELLA = "Cancella tutto";
const ETICHETTA_CONFERMA_CANCELLA = "Sì, cancella tutto";
let cancellazioneArmata = false;

function dimenticaScheda() {
  if (!cancellazioneArmata) {
    cancellazioneArmata = true;
    $("btn-dimentica-scheda").textContent = ETICHETTA_CONFERMA_CANCELLA;
    $("scheda-stato").textContent =
      "Vuoi davvero cancellare tutto quello che VoceAmica ricorda di te? Non si potrà recuperare. " +
      "Premi di nuovo «" + ETICHETTA_CONFERMA_CANCELLA + "» per confermare.";
    return;
  }
  // Invalida un aggiornamento ancora in volo: una scheda cancellata non deve
  // riapparire perché l'archivista ha risposto un secondo dopo.
  generazioneScheda++;
  // «Cancella tutto» deve cancellare tutto: scheda narrativa e prenotazioni ricordate.
  try {
    window.localStorage.removeItem(CHIAVE_SCHEDA);
    window.localStorage.removeItem(CHIAVE_PRENOTAZIONI);
  } catch (e) { /* ignora */ }
  renderScheda("", "Scheda cancellata. Alla prossima chiamata VoceAmica ripartirà da zero.");
}

let generazioneScheda = 0;

/* Secondo ruolo, a chiamata chiusa: riscrive la scheda della persona.
 * Nessuno strumento, nessuna conversazione: produce solo markdown. */
async function aggiornaScheda() {
  const mia = ++generazioneScheda;
  // Il saluto iniziale è già una battuta: senza questo controllo l'archivista
  // riscriverebbe la scheda anche dopo una chiamata in cui Mario non ha parlato.
  const haParlato = sessione.battute.some(function (b) { return b.chi === "mario"; });
  if (!haParlato) {
    renderScheda(caricaScheda(), "In questa chiamata non hai chiesto nulla: la scheda resta invariata.");
    return;
  }
  if (!apiKey) {
    renderScheda(caricaScheda(), "Senza chiave API non posso aggiornare la scheda.");
    return;
  }

  renderScheda(caricaScheda(), "Sto aggiornando la scheda…");

  try {
    const risposta = await chiamaApi({
      system: buildPromptArchivista(),
      maxTokens: 900,
      messages: [{
        role: "user",
        content: buildRichiestaArchivista(
          caricaScheda(), sessione.battute, sessione.prenotazione, sessione.paragrafi
        )
      }]
    });

    if (mia !== generazioneScheda) return;   // cancellata o superata nel frattempo

    const markdown = risposta.content
      .filter(function (b) { return b.type === "text"; })
      .map(function (b) { return b.text; })
      .join("\n")
      .trim();

    if (!markdown) {
      renderScheda(caricaScheda(), "Non sono riuscito a scrivere la scheda: resta quella di prima.");
      return;
    }

    const salvata = salvaScheda(markdown);
    renderScheda(
      markdown,
      salvata
        ? "Scheda aggiornata e salvata in questo browser. Alla prossima chiamata VoceAmica la rileggerà."
        : "Scheda aggiornata, ma non salvata: questo browser non consente l'archiviazione locale."
    );
  } catch (errore) {
    console.error(errore);
    if (mia !== generazioneScheda) return;
    renderScheda(caricaScheda(), "Non sono riuscito ad aggiornare la scheda: resta quella di prima.");
  }
}

function renderScheda(markdown, stato) {
  cancellazioneArmata = false;
  $("btn-dimentica-scheda").textContent = ETICHETTA_CANCELLA;
  $("card-scheda").classList.remove("nascosto");
  $("scheda-stato").textContent = stato;
  $("scheda-testo").textContent = markdown || "(nessuna scheda)";
  $("btn-scarica-scheda").disabled = !markdown;
}

function scaricaScheda() {
  const markdown = $("scheda-testo").textContent;
  if (!markdown || markdown === "(nessuna scheda)") return;

  const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = MARIO.nome.toLowerCase().replace(/\s+/g, "-") + ".md";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/* ================================================================ AVVIO = */

if (window.speechSynthesis) {
  caricaVoci();
  window.speechSynthesis.onvoiceschanged = caricaVoci;
}
document.addEventListener("DOMContentLoaded", init);
