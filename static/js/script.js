document.addEventListener('DOMContentLoaded', function() {
    const timerDisplay = document.getElementById('timer-display');
    const startButton = document.getElementById('start-button');
    const scoreDisplay = document.getElementById('score');
    const controlsDiv = document.getElementById('controls'); // Get controls div
    const bodyElement = document.body;
    const bgSelect = document.getElementById('bg-select');
    let timerInterval = null; // Inizializza a null

    // ... (Funzioni formatTime, updateTimer, applyBackground, backgroundsListIncludes come prima) ...
    // Assicurati che updateTimer usi innerHTML per timerDisplay
    // function formatTime(...) { ... }
    // function updateTimer() { ... timerDisplay.innerHTML = formatTime(data.time_remaining); ... }

    // --- Gestione Pulsante Avvio ---
    if (startButton) {
        startButton.addEventListener('click', function() {
            startButton.disabled = true; // Disabilita subito
            fetch('/start_timer', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log("Timer avviato con successo dal server.");
                        // Aggiorna subito il display e lo stato visivo
                        if (controlsDiv) {
                            controlsDiv.innerHTML = "<p>Sessione di studio in corso...</p>";
                        }
                        // Chiamata immediata per mostrare il tempo e verificare lo stato
                        updateTimer();
                        // Avvia l'intervallo *dopo* la prima chiamata
                        if (timerInterval) clearInterval(timerInterval); // Pulisci intervalli precedenti se esistono
                        timerInterval = setInterval(updateTimer, 1000);
                    } else {
                        console.error("Errore avvio timer:", data.error);
                        alert("Impossibile avviare il timer: " + (data.error || 'Errore sconosciuto'));
                        startButton.disabled = false; // Riabilita se fallisce
                    }
                })
                .catch(error => {
                    console.error('Errore fetch /start_timer:', error);
                    alert("Errore di comunicazione con il server per avviare il timer.");
                    startButton.disabled = false; // Riabilita in caso di errore
                });
        });
    }

    // --- Gestione Selezione Sfondo (come prima) ---
    if (bgSelect) {
        // ... (codice per applyBackground, event listener 'change', caricamento da localStorage) ...
         // Funzione helper per controllare se il valore salvato è tra quelli disponibili
         const availableBackgrounds = ['default', 'forest', 'space', 'abstract'];
         function backgroundsListIncludes(value) {
              return availableBackgrounds.includes(value);
         }
         // Funzione per applicare la classe dello sfondo
         function applyBackground(backgroundValue) {
             // Rimuovi classi bg- precedenti
             bodyElement.className = bodyElement.className.replace(/\bbg-\S+/g, '');
             // Aggiungi la nuova classe (o default)
             bodyElement.classList.add(`bg-${backgroundValue || 'default'}`);
         }
         // Event listener e caricamento localStorage... (vedi codice risposta precedente)
           bgSelect.addEventListener('change', function() { /* ... applyBackground ... localStorage.setItem ... */ });
           let savedBg = null; try { savedBg = localStorage.getItem('backgroundPreference'); } catch(e){}
           if (savedBg && backgroundsListIncludes(savedBg)) { bgSelect.value = savedBg; applyBackground(savedBg); }
           else { const defaultBg = 'default'; bgSelect.value = defaultBg; applyBackground(defaultBg); }

    } else {
        // Se il selettore non esiste, applica comunque il default
        bodyElement.classList.add('bg-default');
    }


    // --- Aggiornamento Iniziale e Periodico ---
    // Chiama subito updateTimer per ottenere lo stato corrente (tempo, stato running)
    updateTimer();

    // Controlla se il timer dovrebbe essere già in esecuzione (basato sull'assenza del bottone Start)
    // e avvia l'intervallo SOLO se non è già stato avviato dal click
    if (!startButton && !timerInterval) {
         // Verifica ulteriore se il server dice che è in esecuzione
         fetch('/get_time').then(res => res.json()).then(data => {
             if(data.timer_running && !timerInterval) {
                 console.log("Timer già in corso (rilevato al caricamento), avvio aggiornamento periodico.");
                 timerInterval = setInterval(updateTimer, 1000);
             } else if (!data.timer_running && timerInterval) {
                 // Se il server dice che NON è in corso, ma abbiamo un intervallo, fermalo.
                 clearInterval(timerInterval);
                 timerInterval = null;
             }
         }).catch(e => console.error("Errore nel check iniziale get_time:", e));
    }

}); // Fine DOMContentLoaded