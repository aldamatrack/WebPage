async function handleSessionAction(action) {
    const sessionId = document.getElementById('session_id').value;
    document.getElementById('output').textContent = '';

    if (!sessionId) {
        alert('Please enter a Session ID.');
        return;
    }

    try {
        const endpoint = action === 'clean' ? '/run-clean-session' : '/run-reset-session';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
            
        });
        console.log(response)

        if (response.ok) {
            const result = await response.json();

            if (result.returncode === 0) {
                document.getElementById('output').textContent = result.output || 'No output';
            } else {
                alert(`Command Error: ${result.error || 'Unknown error occurred'}`);
            }
        } else {
            const error = await response.json();
            alert(`Server Error: ${error.error || 'Unknown server error occurred'}`);
        }
    } catch (err) {
        alert(`Network Error: ${err.message}`);
    }
}

function returnToMainPage() {
    window.location.href = '/index.html';  //Pushing content to production take on mind working directory as root "/" for testing in windows use /MainPage/HTML/index.html
}


document.getElementById('cleanSessionBtn').addEventListener('click', () => handleSessionAction('clean'));
document.getElementById('resetSessionBtn').addEventListener('click', () => handleSessionAction('reset'));

