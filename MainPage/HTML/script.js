function changeMonth(id){
    var tabs = document.querySelectorAll('.calendar-months');
    for(var i = 0; i<tabs.length; i++){
        tabs[i].classList.remove('active');
    }
    document.getElementById(id).classList.add('active');
    console.log("changing quater");
}

function showTableContent(id) {
    var tableContent = document.querySelectorAll('.table-info');

    for (var i = 0; i < tableContent.length; i++) {
        tableContent[i].classList.remove('active'); 

        if (tableContent[i].id == id) {
            tableContent[i].classList.add('active'); 
        }
    }
}

function redirectToPage() {
    window.location.href = '/MonthlyReport/index/index.html'; // Relative URL on the same server
}

function loginPage() {
    window.location.href = '/Login/index.html'
}

function sessionCleanerPage(){
    window.location.href = '/ControllerManager/index.html'
}

