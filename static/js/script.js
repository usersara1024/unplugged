document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM Caricato. Inizio esecuzione script."); // Log iniziale

    // --- Elementi DOM ---
    const timerDisplay = document.getElementById('timer-display');
    const startButton = document.getElementById('start-button');
    const scoreDisplay = document.getElementById('score');
    const controlsDiv = document.getElementById('controls');
    const bodyElement = document.body;
    const bgSelect = document.getElementById('bg-select');
    let timerInterval = null; // Variabile per l'intervallo

    // --- Controllo Elementi Essenziali ---
    if (!timerDisplay) console.error("ERRORE: Elemento timer-display non trovato!");
    if (!bodyElement) console.error("ERRORE: Elemento body non trovato!");
    // Non è un errore se startButton o bgSelect non ci sono (dipende dallo stato)
    if (startButton) console.log("Pulsante Start trovato.");
    else console.log("Pulsante Start NON trovato (timer forse già attivo?).");
    if (bgSelect) console.log("Selettore Sfondo trovato.");
    else console.log("Selettore Sfondo NON trovato.");


    // --- Funzioni ---

    // Funzione per formattare il tempo (MM:SS)
    function formatTime(seconds) {
        if (isNaN(seconds) || seconds < 0) {
            return "--:--";
        }
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
    }

    // Funzione per aggiornare il timer (chiamata a /get_time)
    function updateTimer() {
        console.log("Chiamata a updateTimer..."); // Log chiamata funzione
        if (!timerDisplay) return; // Non fare nulla se il display non esiste

        fetch('/get_time')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Errore HTTP ${response.status} da /get_time`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Dati ricevuti da /get_time:", data); // Log dati ricevuti
                if (data.error) {
                    console.error("Errore dal server (/get_time):", data.error);
                    if (timerInterval) clearInterval(timerInterval);
                    timerDisplay.innerHTML = "Errore Server";
                    return;
                }

                // Aggiorna display tempo
                timerDisplay.innerHTML = formatTime(data.time_remaining);

                // Aggiorna punteggio (se presente)
                if (scoreDisplay && data.score !== undefined) {
                     scoreDisplay.innerText = data.score;
                }

                // Gestione fine timer e reindirizzamento
                if (data.should_redirect && data.redirect_url) {
                    console.log("Tempo scaduto o reindirizzamento richiesto dal server. Vado a:", data.redirect_url);
                    if (timerInterval) clearInterval(timerInterval);
                    timerInterval = null;
                    window.location.href = data.redirect_url; // Reindirizza!
                } else if (!data.timer_running) {
                    // Se il timer NON è in esecuzione e NON dobbiamo reindirizzare
                    console.log("Il server indica che il timer non è in esecuzione.");
                    if (timerInterval) {
                        console.log("Fermo l'intervallo timer client.");
                        clearInterval(timerInterval);
                        timerInterval = null;
                    }
                    // Riattiva il pulsante Start se esiste e non è già attivo
                    if (startButton && startButton.disabled) {
                        console.log("Riattivo il pulsante Start.");
                        startButton.disabled = false;
                    }
                     // Assicurati che il messaggio "in corso" sia rimosso se il bottone riappare
                    if (controlsDiv && startButton) {
                         if (!controlsDiv.contains(startButton)) {
                             controlsDiv.innerHTML = ''; // Pulisci
                             controlsDiv.appendChild(startButton); // Rimetti il bottone
                         }
                    }

                } else {
                     // Il timer è in esecuzione secondo il server
                     console.log("Il server indica che il timer è in esecuzione.");
                }
            })
            .catch(error => {
                console.error('Errore grave durante fetch /get_time:', error);
                if (timerDisplay) timerDisplay.innerHTML = "Errore Rete";
                if (timerInterval) clearInterval(timerInterval);
                timerInterval = null;
            });
    }

    // Funzione per applicare lo sfondo (SOLO cambio classe, senza localStorage per ora)
    function applyBackground(backgroundValue) {
         const valueOrDefault = backgroundValue || 'default';
         console.log("Applico sfondo:", valueOrDefault);
         // Rimuovi classi bg- precedenti
         bodyElement.className = bodyElement.className.replace(/\bbg-\S+/g, '');
         // Aggiungi la nuova classe
         bodyElement.classList.add(`bg-${valueOrDefault}`);
    }

    // --- Logica Esecuzione Iniziale ---

    // 1. Gestione Sfondo Iniziale e Selezione
    if (bgSelect) {
        // Lista sfondi (deve corrispondere ai valori 'value' e classi CSS)
         const availableBackgrounds = ['abstract', 'forest', 'space', 'default'];

         // Imposta lo sfondo iniziale su 'default' o sul valore selezionato se valido
         let initialBg = bgSelect.value;
         if (!availableBackgrounds.includes(initialBg)) {
             console.warn(`Valore iniziale sfondo '${initialBg}' non valido, uso default.`);
             initialBg = 'Abstract';
             bgSelect.value = initialBg; // Aggiorna il dropdown
         }
         applyBackground(initialBg);

        // Listener per cambi futuri
        bgSelect.addEventListener('change', function() {
            if (availableBackgrounds.includes(this.value)) {
                applyBackground(this.value);
                // Qui potresti riattivare localStorage se necessario:
                // try { localStorage.setItem('backgroundPreference', this.value); } catch(e){}
            } else {
                 console.warn(`Valore selezionato '${this.value}' non valido.`);
                 applyBackground('Abstract'); // Fallback a default
                 this.value = 'Abstract'; // Resetta dropdown
            }
        });
         console.log("Listener per cambio sfondo aggiunto.");
    } else {
         // Se non c'è selettore, applica default
         applyBackground('Abstract');
    }


    // 2. Gestione Avvio Timer tramite Pulsante
    if (startButton) {
        startButton.addEventListener('click', function() {
            console.log("Click su Start rilevato.");
            startButton.disabled = true;
            if (controlsDiv) controlsDiv.innerHTML = "<p>Avvio sessione...</p>"; // Messaggio temporaneo

            fetch('/start_timer', { method: 'POST' })
                .then(response => {
                    if (!response.ok) throw new Error(`Errore HTTP ${response.status} da /start_timer`);
                    return response.json();
                })
                .then(data => {
                    console.log("Risposta da /start_timer:", data);
                    if (data.success) {
                        console.log("Avvio timer Riuscito.");
                        if (controlsDiv) controlsDiv.innerHTML = "<p>Puoi utilizzare il cellulare...</p>";

                        // Pulisci intervalli vecchi e avvia quello nuovo
                        if (timerInterval) clearInterval(timerInterval);
                        timerInterval = setInterval(updateTimer, 1000);

                        // Chiama subito update per aggiornare il display immediatamente
                        updateTimer();

                    } else {
                        console.error("Avvio timer Fallito:", data.error);
                        alert("Impossibile avviare il timer: " + (data.error || 'Errore sconosciuto'));
                        startButton.disabled = false; // Riabilita
                        if (controlsDiv) controlsDiv.innerHTML = ''; controlsDiv.appendChild(startButton); // Rimetti bottone
                    }
                })
                .catch(error => {
                    console.error('Errore grave fetch /start_timer:', error);
                    alert("Errore di comunicazione con il server per avviare il timer.");
                    startButton.disabled = false;
                     if (controlsDiv) controlsDiv.innerHTML = ''; controlsDiv.appendChild(startButton); // Rimetti bottone
                });
        });
    }

    // 3. Aggiornamento Iniziale e Avvio Intervallo (se timer già attivo)
    console.log("Eseguo updateTimer iniziale...");
    updateTimer(); // Chiamata per ottenere stato iniziale e tempo

    // Se il pulsante NON esiste, significa che la pagina è stata caricata
    // con il timer già attivo lato server. Avviamo l'intervallo client.
    if (!startButton && !timerInterval) {
         console.log("Pulsante non trovato, presumo timer già attivo. Avvio intervallo client.");
         timerInterval = setInterval(updateTimer, 1000);
    }

    console.log("Fine inizializzazione script.");

}); // Fine DOMContentLoaded