document.addEventListener('DOMContentLoaded', function() {
    const timerDisplay = document.getElementById('timer-display');
    const startButton = document.getElementById('start-button');
    const scoreDisplay = document.getElementById('score'); // Get score element
    let timerInterval; // Variabile per memorizzare l'intervallo del timer

    // Funzione per formattare il tempo (MM:SS)
    function formatTime(seconds) {
        if (isNaN(seconds) || seconds < 0) {
            return "--:--";
        }
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `<span class="math-inline">\{String\(minutes\)\.padStart\(2, '0'\)\}\:</span>{String(remainingSeconds).padStart(2, '0')}`;
    }

    // Funzione per aggiornare il timer sul client e chiedere al server
    function updateTimer() {
        fetch('/get_time') // Chiedi al server lo stato aggiornato
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Errore HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    console.error("Errore dal server:", data.error);
                    clearInterval(timerInterval); // Ferma il timer in caso di errore
                    timerDisplay.innerText = "Errore";
                    return;
                }

                // Aggiorna il display con il tempo ricevuto dal server
                timerDisplay.innerText = formatTime(data.time_remaining);
                // Aggiorna anche il punteggio se presente
                if (scoreDisplay && data.score !== undefined) {
                     scoreDisplay.innerText = data.score;
                }


                // Gestione fine timer e reindirizzamento richiesto dal server
                if (data.should_redirect && data.redirect_url) {
                    console.log("Tempo scaduto o reindirizzamento richiesto. Vado a:", data.redirect_url);
                    clearInterval(timerInterval); // Ferma il timer prima di reindirizzare
                    window.location.href = data.redirect_url; // Reindirizza alla pagina delle domande
                } else if (!data.timer_running) {
                    // Se il timer non è più in esecuzione (ma non dobbiamo reindirizzare), ferma l'intervallo
                    console.log("Timer fermato dal server.");
                    clearInterval(timerInterval);
                    if(startButton) startButton.disabled = false; // Riabilita il pulsante se esiste
                }

            })
            .catch(error => {
                console.error('Errore durante fetch /get_time:', error);
                timerDisplay.innerText = "Errore";
                clearInterval(timerInterval); // Ferma il timer in caso di errore di rete/fetch
            });
    }

    // --- Gestione Pulsante Avvio ---
    if (startButton) {
        startButton.addEventListener('click', function() {
            startButton.disabled = true; // Disabilita subito per evitare doppi click
            fetch('/start_timer', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log("Timer avviato con successo dal server.");
                        timerDisplay.innerText = formatTime(data.time_remaining); // Mostra tempo iniziale
                        // Avvia l'intervallo di aggiornamento solo se il timer è partito con successo
                        timerInterval = setInterval(updateTimer, 1000);
                        // Nascondi il pulsante e mostra messaggio "in corso" (opzionale)
                        const controlsDiv = document.getElementById('controls');
                        if (controlsDiv) {
                            controlsDiv.innerHTML = "<p>Sessione di studio in corso...</p>";
                        }
                    } else {
                        console.error("Errore avvio timer:", data.error);
                        alert("Impossibile avviare il timer: " + data.error);
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

    // --- Aggiornamento Iniziale e Periodico ---
    // Chiama subito updateTimer per ottenere lo stato corrente all'avvio della pagina
    // Questo gestisce anche il caso in cui la pagina venga ricaricata mentre il timer è già attivo
    updateTimer();
    // Imposta l'intervallo solo se il timer NON è già gestito dal click su startButton
    // Controlliamo se l'intervallo è già stato definito (succede se il timer è stato avviato)
    // e se il pulsante start non esiste (significa che il timer era già running al caricamento)
    if (!timerInterval && !startButton) {
         console.log("Timer già in corso al caricamento della pagina, avvio aggiornamento periodico.");
         timerInterval = setInterval(updateTimer, 1000);
    }

    // --- Gestione Selezione Sfondo (Placeholder) ---
    const bgSelect = document.getElementById('bg-select');
    if (bgSelect) {
        bgSelect.addEventListener('change', function() {
            console.log("Sfondo selezionato:", this.value);
            // Qui potresti aggiungere logica per cambiare classe CSS del body:
            // document.body.className = `bg-${this.value}`;
            alert(`Hai selezionato lo sfondo: ${this.value}. La modifica visiva non è implementata.`);
        });
    }

});