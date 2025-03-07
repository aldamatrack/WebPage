async function handleSessionAction(action) {
    const sessionId = document.getElementById('session_id').value.trim();
    const outputElement = document.getElementById('output');
    outputElement.textContent = 'Processing...';

    if (!sessionId) {
        alert('Please enter a Session ID.');
        return;
    }

    try {
        const endpoint = action === 'clean' ? 'http://localhost:5000/run-clean-session' : 'http://localhost:5000/run-reset-session';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId }),
            signal: AbortSignal.timeout(8000)
        });

        // Verificar tipo de contenido
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const textResponse = await response.text();
            throw new Error(`Invalid response: ${textResponse.substring(0, 100)}`);
        }

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Server error');
        }

        if (data.returncode !== 0) {
            outputElement.textContent = `Error: ${data.error}`;
            alert(`Operation failed: ${data.error}`);
        } else {
            outputElement.textContent = data.output || 'Operation completed successfully';
        }
    } catch (err) {
        outputElement.textContent = `Error: ${err.message}`;
        console.error('API Error:', err);
        alert(err.message.includes('Invalid response') ? 'Check server status' : err.message);
    }
}

// Event Listeners
document.getElementById('cleanSessionBtn').addEventListener('click', () => handleSessionAction('clean'));
document.getElementById('resetSessionBtn').addEventListener('click', () => handleSessionAction('reset'));
document.getElementById('Exit').addEventListener('click', () => window.location.href = '/index.html');