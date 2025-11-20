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
        try {
            const data = JSON.parse(line);
            const messageElement = document.createElement('div');
            messageElement.classList.add(data.type);
            messageElement.textContent = data.content;
            gameOutput.appendChild(messageElement);

            if (data.content === 'save_conversation') {
                messageElement.remove();
                const saveButton = document.createElement('button');
                saveButton.textContent = 'Save Conversation';
                saveButton.addEventListener('click', async () => {
                    await fetch('/save_conversation', { method: 'POST' });
                    alert('Conversation saved!');
                    saveButton.disabled = true;
                });
                gameOutput.appendChild(saveButton);
            }
        } catch (e) {
            console.error('Error parsing JSON:', line, e);
        }
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
