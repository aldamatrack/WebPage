// ---- Calendar & Table Helpers ----
function changeMonth(id) {
    const tabs = document.querySelectorAll('.calendar-months');
    tabs.forEach(tab => tab.classList.remove('active'));
    const target = document.getElementById(id);
    if (target) target.classList.add('active');
    console.log("changing quarter to", id);
}

function showTableContent(id) {
    const tableContent = document.querySelectorAll('.table-info');
    tableContent.forEach(block => {
        block.classList.toggle('active', block.id === id);
    });
}

// ---- Navigation ----
function redirectToPage() {
    window.location.href = '/monthlyreport';
}

function loginPage() {
    window.location.href = '/login';
}

function sessionCleanerPage() {
    window.location.href = '/controler';
}

function pduPage() {
    window.location.href = '/pdu';
}

function returnToMainPage() {
    window.location.href = '/';
}

// ---- Login Stub ----
async function login() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
  
    try {
      const res = await fetch("/api/PDUauthentication");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
  
      // flatten and trim
      const users = data.authUsers.map(u => String(u[0]).trim());
      const fixedPass = String(data.PDUpass).trim();
  
  
      if (users.includes(username) && password === fixedPass) {
        localStorage.setItem('loggedIn', 'true');
        alert("Login successful");
        window.location.href = '/pdu';
      } else {
        alert("Invalid username or password, redirecting to main page");
        window.location.href = '/';
      }
    } catch (err) {
      console.error("Login error:", err);
      alert("An error occurred during login.");
    }
  }

  async function loginController() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
  
    try {
      const res = await fetch("/api/Controllerauthentication");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
  
      // flatten and trim
      const users = data.authUsers.map(u => String(u[0]).trim());
      const fixedPass = String(data.Controllerpass).trim();

  
      if (users.includes(username) && password === fixedPass) {
        localStorage.setItem('loggedIn', 'true');
        alert("Login successful");
        window.location.href = '/controler';
      } else {
        alert("Invalid username or password, redirecting to main page");
        window.location.href = '/';
      }
    } catch (err) {
      console.error("Login error:", err);
      alert("An error occurred during login.");
    }
  }


// ---- Session Cleaner with Confirmation Prompt ----
async function handleSessionAction(action) {
    const sessionId = document.getElementById('session_id')?.value.trim();
    const outputEl = document.getElementById('output');
    if (!sessionId) {
        alert('Please enter a Session ID.');
        return;
    }

    outputEl.textContent = 'Processing...';

    const endpoint = action === 'clean'
        ? '/run-clean-session'
        : '/run-reset-session';

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });

        const data = await res.json();

        if (res.status !== 200 || data.error) {
            outputEl.textContent = `Error: ${data.error || 'Unknown error'}`;
            return;
        }

        // Display the VM's message
        outputEl.textContent = data.output || 'Waiting for confirmation...';

        // Show native confirm popup
        const userConfirmed = window.confirm(
            `VM Response:\n\n${data.output}\n\nDo you want to continue?`
        );

        const answer = userConfirmed ? 'y' : 'n';

        // Send confirmation
        await sendConfirmation(sessionId, answer);

    } catch (err) {
        console.error("Session action error:", err);
        outputEl.textContent = `Error: ${err.message}`;
    }
}

async function sendConfirmation(sessionId, answer) {
    const outputEl = document.getElementById('output');
    outputEl.textContent = 'Sending confirmation...';

    try {
        const res = await fetch('/confirm-session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                confirmation: answer
            })
        });

        const data = await res.json();
        if (res.status !== 200 || data.error) {
            outputEl.textContent = `Error: ${data.error || 'Unknown error'}`;
            return;
        }

        outputEl.textContent = data.result || 'Command completed.';
    } catch (err) {
        outputEl.textContent = `Error: ${err.message}`;
    }
}
// ---- PDU Data Fetching ----
function fetchData() {
    fetch('/data')
        .then(res => res.json())
        .then(populateTable)
        .catch(err => {
            console.error('Error fetching data:', err);
            alert('Error fetching data');
        });
}

function populateTable(data) {
    const tableHeader = document.getElementById('table-header');
    const tableBody   = document.getElementById('table-body');
    if (!tableHeader || !tableBody) return;

    // Headers
    tableHeader.innerHTML = '';
    const headers = ['pdu_number','ipaddress','pduname','datacenter','owner','description','status','actions'];
    const headerRow = document.createElement('tr');
    headers.forEach(h => {
        const th = document.createElement('th');
        th.textContent = h;
        headerRow.appendChild(th);
    });
    tableHeader.appendChild(headerRow);

    // Rows
    tableBody.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        headers.forEach(field => {
            const td = document.createElement('td');
            if (field !== 'actions') {
                td.textContent = row[field];
                td.contentEditable = (field === 'ipaddress');
                td.dataset.field = field;
                td.dataset.pduname = row.pduname;
                tr.appendChild(td);
            } else {
                const btn = document.createElement('button');
                btn.textContent = 'Update';
                btn.addEventListener('click', () => updateData(tr));
                const actionTd = document.createElement('td');
                actionTd.appendChild(btn);
                tr.appendChild(actionTd);
            }
        });
        tableBody.appendChild(tr);
    });
}

function updateData(row) {
    const pduname   = row.querySelector('[data-field="pduname"]').textContent;
    const ipaddress = row.querySelector('[data-field="ipaddress"]').textContent;

    fetch('/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pduname, ipaddress })
    })
    .then(res => {
        if (!res.ok) throw new Error('Update failed');
        return res.json();
    })
    .then(() => alert('IP address updated successfully'))
    .catch(err => {
        console.error('Error updating data:', err);
        alert('Error updating data: ' + err.message);
    });
}

// ---- Hover Popups ----
function initHoverPopups() {
    const hoverEls = document.querySelectorAll('.hover-element');
    hoverEls.forEach(el => {
        const popup = el.querySelector('.image-popup');
        el.addEventListener('mouseenter', () => popup.style.display = 'block');
        el.addEventListener('mouseleave', () => popup.style.display = 'none');
    });
    document.addEventListener('click', event => {
        hoverEls.forEach(el => {
            const popup = el.querySelector('.image-popup');
            if (!el.contains(event.target) && popup && !popup.contains(event.target)) {
                popup.style.display = 'none';
            }
        });
    });
}

// ---- Global Event Binding ----
document.addEventListener('DOMContentLoaded', () => {
    // Navigation buttons (if present)
    document.getElementById('cleanSessionBtn')?.addEventListener('click', () => handleSessionAction('clean'));
    document.getElementById('resetSessionBtn')?.addEventListener('click', () => handleSessionAction('reset'));
    document.getElementById('Exit')?.addEventListener('click', returnToMainPage);

    // Hover popups
    initHoverPopups();

    // Only fetch PDU data when table elements exist
    if (document.getElementById('table-header') && document.getElementById('table-body')) {
        fetchData();
    }
});

document.getElementById('cleanSessionBtn').addEventListener('click', () => handleSessionAction('clean'));
document.getElementById('resetSessionBtn').addEventListener('click', () => handleSessionAction('reset'));

