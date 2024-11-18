
document.addEventListener('DOMContentLoaded', function () {
    // Select all product card wrappers
    const productCards = document.querySelectorAll('#product-card-wrapper');

    productCards.forEach(card => {
        const details = card.querySelector('#details');

        const summary = details.querySelector('#details-summary');

        // When mouse enters the card
        summary.addEventListener('mouseenter', function () {
            details.open = true; // Keep details open

            // Set a timeout to close the details after 5 seconds
            timeoutId = setTimeout(() => {
                details.open = false;
            }, 5000);
        });

        // When mouse leaves the card
        card.addEventListener('mouseleave', function () {
            // Clear the timeout if the mouse leaves the card
            clearTimeout(timeoutId);
            // Close the details
            details.open = false;
        });
    });
});
