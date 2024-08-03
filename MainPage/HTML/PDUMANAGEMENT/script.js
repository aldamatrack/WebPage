document.addEventListener('DOMContentLoaded', (event) => {
    fetchData();
});

function returnToMainPage() {
    window.location.href = '/MainPage/HTML/index.html';  //Pushing content to production take on mind working directory as root "/" for testing in windows use /MainPage/HTML/index.html
}

function fetchData() {
    fetch('http://127.0.0.1:5000/data')
        .then(response => response.json())
        .then(data => populateTable(data))
        .catch(error => {
            console.error('Error fetching data:', error);
            alert('Error fetching data');
        });
}

function populateTable(data) {
    const tableHeader = document.getElementById('table-header');
    const tableBody = document.getElementById('table-body');

    // Clear existing content
    tableHeader.innerHTML = '';
    tableBody.innerHTML = '';

    // Create table headers
    const headers = ['pdu_number', 'ipaddress', 'pduname', 'datacenter', 'owner', 'description','actions'];
    const headerRow = document.createElement('tr');
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    tableHeader.appendChild(headerRow);

    // Create table rows
    data.forEach(row => {
        const tr = document.createElement('tr');
        headers.forEach(header => {
            if (header !== 'actions') {
                const td = document.createElement('td');
                td.textContent = row[header];
                td.contentEditable = header === 'ipaddress'; // Allow editing only for ipaddress
                td.dataset.field = header;
                td.dataset.pduname = row.pduname;
                tr.appendChild(td);
            } else {
                const actionTd = document.createElement('td');
                const updateButton = document.createElement('button');
                updateButton.textContent = 'Update';
                updateButton.addEventListener('click', () => updateData(tr));
                actionTd.appendChild(updateButton);
                tr.appendChild(actionTd);
            }
        });
        tableBody.appendChild(tr);
    });
}

function updateData(row) {
    const pduname = row.querySelector('[data-field="pduname"]').textContent;
    const ipaddress = row.querySelector('[data-field="ipaddress"]').textContent;

    const data = {
        pduname: pduname,
        ipaddress: ipaddress
    };

    fetch('http://127.0.0.1:5000/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {
                throw new Error(errorData.message);
            });
        }
        return response.json();
    })
    .then(result => {
        console.log(result.message);
        alert('IP address updated successfully');
    })
    .catch(error => {
        console.error('Error updating data:', error);
        alert('Error updating data: ' + error.message);
    });
}
