$(document).ready(function(){
var productForm = $(".form-product-ajax")
productForm.submit(function(event){
    console.log("form submit")
  event.preventDefault();
  var thisForm = $(this)
  var method = thisForm.attr("method")
  var url = thisForm.attr("action")
  var formData = thisForm.serialize()
  $.ajax({
    url: url,
    method: method,
    data: formData,
    success: function(formData){
      var productAction = thisForm.find(".product-action")
      if (formData.added){
        console.log("added")
        productAction.html(
          "<button type='submit' class='btn btn-link' style='padding:0px'>Remove</button>")
      } else{
        console.log("removed")
          productAction.html(
            "<button type='submit' class='btn btn-success'>Add to cart!</button>")
      }
      cartCounter = $(".navbar-cart-counter")
      console.log(cartCounter)
      cartCounter.text(formData.cart_count)

      var currentPath = window.location.href
      if (currentPath.indexOf('cart') !== -1){
        updateCart()
      }
    },
    error: function(error){
      console.log("error")
      console.log(error)
    },
  })
})

function updateCart(){
    var method = "GET";
    var cartBody = $(".cart-body")
    var cartBody = $(".cart-body")
    var cartProductRows = cartBody.find(".cart-product-rows")
    var cartItemRemoveForm= $(".cart-item-remove-form")
    var data = {}
    $.ajax({
      url: '/cart/api-cart',
      method: "GET",
      data: data,
      success: function(data){
        cartProductRows.html('')
        i = data.products.length
        console.log(data.products)
        $.each(data.products, function(index, value){
          var newCartItemRemoveForm = cartItemRemoveForm.clone()
          newCartItemRemoveForm.css('display', 'block')
          newCartItemRemoveForm.find(".product_id").val(value.id)
          cartBody.prepend(
            "<tr><th scope='row'>" + i + "</th><td><a href='" + value.url +
            "'>" + value.name + "</a>" + newCartItemRemoveForm.html() +
            "</td><td>" + value.price + "</td></tr>");
          i--;
        })
        cartBody.find(".cart-total").text(data.total)
      },
      error:  function(error){
        console.log('error')
        console.log(error)
      }
    })
  }
})

// Hide flash-messages after peeriod of time
document.addEventListener('DOMContentLoaded', function() {
    showPopUpBox("flashes")
  }, false);

 function showPopUpBox(id) {
       var e = document.getElementById(id);
       e.classList.add("show");
       setTimeout(function() {
         document.getElementById( "flashes" ).classList.remove('show');
         document.getElementById( "flashes" ).classList.add('hide');
       }, 5000);
    };

// Save in session flash messages from JS
  function update_messages(messages){
  $("#flashes").html("");
  $("#flashes").append("<ul class='messages flashes' id='popup-messages-content'></ul>");
  console.log($("#flashes"));
  $.each(messages, function (i, m) {
                  $("#popup-messages-content").append("<li><div class='alert alert-"+m.level+"''>"+m.message+"</div></li>");
              });
            }


// Extract form session flash messages that were sent from JS
  window.onload = function() {

      var message =  sessionStorage.getItem("message");
      console.log(message);
      if (message) {
          var message = [{"message": message}];
          var level =  sessionStorage.getItem("level");
          if (level) {
            message["level"] = level;
            sessionStorage.removeItem("level");
          }
          update_messages(message);
          sessionStorage.removeItem("message");
      }
  }
