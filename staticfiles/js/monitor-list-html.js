
document.addEventListener('DOMContentLoaded', function () {
    // Select all product card wrappers
    const productCards = document.querySelectorAll('.product-card-wrapper');

    productCards.forEach(card => {
        const details = card.querySelector('#details');

        // When mouse enters the card
        card.addEventListener('mouseenter', function () {
            details.open = true; // Keep details open
        });

        // When mouse leaves the card
        card.addEventListener('mouseleave', function () {
            details.open = false; // Close details
        });
    });
});
