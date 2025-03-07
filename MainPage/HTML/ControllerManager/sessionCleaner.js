async function handleSessionAction(action) {
    const sessionId = document.getElementById('session_id').value.trim();
    const outputElement = document.getElementById('output');
    outputElement.textContent = 'Processing...';

    if (!sessionId) {
        alert('Please enter a Session ID.');
        return;
    }

    try {
        // Asegúrate de que la URL sea correcta
        const endpoint = action === 'clean' 
            ? 'http://localhost:5000/run-clean-session' 
            : 'http://localhost:5000/run-reset-session';

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId }),
        });

        // Manejar respuestas no JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error(`Server responded with: ${text.substring(0, 100)}`);
        }

        const data = await response.json();
        
        if (data.returncode !== 0) {
            outputElement.textContent = `Error: ${data.error}`;
        } else {
            outputElement.textContent = data.output || 'Success!';
        }
    } catch (err) {
        outputElement.textContent = `Error: ${err.message}`;
        console.error("Detalle del error:", err);
    }
}
// Event Listeners
document.getElementById('cleanSessionBtn').addEventListener('click', () => handleSessionAction('clean'));
document.getElementById('resetSessionBtn').addEventListener('click', () => handleSessionAction('reset'));
document.getElementById('Exit').addEventListener('click', () => window.location.href = '/index.html');