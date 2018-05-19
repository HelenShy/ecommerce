var paymentForm = $(".payment-form")
if (paymentForm.length == 1) {
  var PubKey = paymentForm.attr("data_token")
  var nextUrl = paymentForm.attr("data-next-url")
// Create a Stripe client.
var stripe = Stripe(PubKey);

// Create an instance of Elements.
var elements = stripe.elements();

// Custom styling can be passed to options when creating an Element.
// (Note that this demo uses a wider set of styles than the guide below.)
var style = {
base: {
  color: '#32325d',
  lineHeight: '18px',
  fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
  fontSmoothing: 'antialiased',
  fontSize: '16px',
  '::placeholder': {
    color: '#aab7c4'
  }
},
invalid: {
  color: '#fa755a',
  iconColor: '#fa755a'
}
};

// Create an instance of the card Element.
var card = elements.create('card', {style: style});

// Add an instance of the card Element into the `card-element` <div>.
card.mount('#card-element');

// Handle real-time validation errors from the card Element.
card.addEventListener('change', function(event) {
var displayError = document.getElementById('card-errors');
if (event.error) {
  displayError.textContent = event.error.message;
} else {
  displayError.textContent = '';
}
});

// Handle form submission.
var form = document.getElementById('payment-form');
form.addEventListener('submit', function(event) {
event.preventDefault();

stripe.createToken(card).then(function(result) {
  if (result.error) {
    // Inform the user if there was an error.
    var errorElement = document.getElementById('card-errors');
    errorElement.textContent = result.error.message;
  } else {
    // Send the token to your server.
    stripeTokenHandler(result.token);
  }
});
});
}
else{
  console.log(paymentForm.length)
}


function stripeTokenHandler(token) {
  var form = document.getElementById('payment-form');
  var endpoint = "/billing/payment/create/"
  var data = {
    'token': token.id
  }
  $.ajax({
    url: endpoint,
    method: "POST",
    data: data,
    success: function(data){
      card.clear()
      if (nextUrl) {
        sessionStorage.setItem('message', data.message || 'SUCCESS');
        sessionStorage.setItem('level', 'SUCCESS');
        window.location.href = nextUrl;
      }
      else {
        update_messages([{"message": data.message, "level": 'SUCCESS'}]);
        showPopUpBox("flashes");
      }
    },
    error:  function(error){
      sessionStorage.setItem('message', data.message || 'ERROR');
      sessionStorage.setItem('level', 'ERROR');
      window.location.reload();
    }
  })
}
