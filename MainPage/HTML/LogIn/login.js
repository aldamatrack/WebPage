function login() {
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    // Replace with your authentication logic
    if (username === 'admin' && password === 'admin') {
        localStorage.setItem('loggedIn', 'true');
        alert("login succesull")
        window.location.href = '../PDUMANAGEMENT/index.html';
    } else {
        alert("Invalid username or password, redirecting to main page")
        window.location.href = '../index.html'
    }
}