document.addEventListener('DOMContentLoaded', function () {
    var stripe = Stripe(stripePublicKey);
    var elements = stripe.elements();
    var card = elements.create('card');
    card.mount('#card-element');

    card.addEventListener('change', function (event) {
        var displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
    });

    var form = document.getElementById('payment-form');

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        form.querySelector('button').disabled = true;

        stripe.createToken(card).then(function (result) {
            if (result.error) {
                var errorElement = document.getElementById('card-errors');
                errorElement.textContent = result.error.message;
                form.querySelector('button').disabled = false;
            } else {
                stripeTokenHandler(result.token);
            }
        });
    });

    function stripeTokenHandler(token) {
        // Create a hidden input element to hold the token
        var hiddenInput = document.createElement('input');
        hiddenInput.setAttribute('type', 'hidden');
        hiddenInput.setAttribute('name', 'stripeToken');
        hiddenInput.setAttribute('value', token.id);
    
        // Append the hidden input to the form
        form.appendChild(hiddenInput);
    
        // Submit the form
        form.submit();
    }
    

    // Enable the submit button initially
    form.querySelector('button').disabled = false;
});
