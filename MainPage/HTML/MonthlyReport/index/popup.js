document.addEventListener('DOMContentLoaded', function () {
    const hoverElements = document.querySelectorAll('.hover-element');

    hoverElements.forEach(element => {
        element.addEventListener('mouseenter', function () {
            const imagePopup = this.querySelector('.image-popup');
            imagePopup.style.display = 'block';
        });

        element.addEventListener('mouseleave', function () {
            const imagePopup = this.querySelector('.image-popup');
            imagePopup.style.display = 'none';
        });
        
    });

    // Optional: Close popup if user clicks anywhere outside the popup
    document.addEventListener('click', function (event) {
        hoverElements.forEach(element => {
            const imagePopup = element.querySelector('.image-popup');
            if (!element.contains(event.target) && !imagePopup.contains(event.target)) {
                imagePopup.style.display = 'none';
            }
        });
        
    });
});



function returnToMainPage() {
    window.location.href = 'index.html';  //Pushing content to production take on mind working directory as root "/" for testing in windows use /MainPage/HTML/index.html
}
