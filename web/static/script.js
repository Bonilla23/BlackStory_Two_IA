document.getElementById('game-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const form = this;
    const submitButton = form.querySelector('button[type="submit"]');
    submitButton.disabled = true;

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    const gameOutput = document.getElementById('game-output');
    gameOutput.innerHTML = '<div class="event">Starting game...</div>';

    const response = await fetch('/start_game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    gameOutput.innerHTML = '';

    const processLine = (line) => {
        if (line.trim() === '') return;
        
        const messageElement = document.createElement('div');
        // Determine class based on content
        if (line.startsWith('Generando') || line.startsWith('==') || line.startsWith('Narrador:') || line.startsWith('Detective:') || line.startsWith('Dificultad:') || line.startsWith('---') || line.startsWith('Misterio:') || line.startsWith('¡Se ha alcanzado') || line.startsWith('El Detective tiene') || line.startsWith('RESULTADO:') || line.startsWith('HISTORIA ORIGINAL:') || line.startsWith('Situación misteriosa:') || line.startsWith('Solución oculta:') || line.startsWith('SOLUCIÓN DEL DETECTIVE:') || line.startsWith('No se proporcionó') || line.startsWith('VEREDICTO DEL NARRADOR:') || line.startsWith('Veredicto:') || line.startsWith('Análisis:') || line.startsWith('El juego ha terminado')) {
            messageElement.classList.add('event');
        } else if (line.startsWith('Detective:')) {
            messageElement.classList.add('detective');
            line = line.replace('Detective: ', ''); // Remove prefix for display
        } else if (line.startsWith('Narrador:')) {
            messageElement.classList.add('narrator');
            line = line.replace('Narrador: ', ''); // Remove prefix for display
        } else if (line.startsWith('Error')) {
            messageElement.classList.add('error');
        }

        if (line === 'save_conversation') {
            const saveButton = document.createElement('button');
            saveButton.textContent = 'Save Conversation';
            saveButton.addEventListener('click', async () => {
                await fetch('/save_conversation', { method: 'POST' });
                alert('Conversation saved!');
                saveButton.disabled = true;
            });
            gameOutput.appendChild(saveButton);
            return;
        }

        messageElement.textContent = line;
        gameOutput.appendChild(messageElement);
    };

    let buffer = '';
    while (true) {
        const { done, value } = await reader.read();
        if (done) {
            if (buffer) {
                processLine(buffer);
            }
            submitButton.disabled = false;
            break;
        }
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
            processLine(line);
        }
    }
});
