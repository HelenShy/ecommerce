$(document).ready(function(){
var productForm = $(".form-product-ajax")

function productIsPurchased(productId, submitSpan){
    var actionEndpoint = '/orders/verify/ownership/'
    var httpMethod = 'GET'
    var data = {
      product_id: productId
    }

    var isOwner;
    $.ajax({
        url: actionEndpoint,
        method: httpMethod,
        data: data,
        success: function(data){
          console.log(data)
          console.log(data.owner)
          if (data.owner){
            isOwner = true
            submitSpan.html("<p>Already in <a  href='/purchases/'>purchased</a></p>")
          } else {
            isOwner = false
          }
        },
        error: function(error){
        }
    })
    return isOwner
};

$.each(productForm, function(index, value){
  $this = $(this);
  var productAction = $this.find(".product-action");
  var productInput = $this.find("[name='product_id']");
  var productId = productInput.attr("value");
  var isPurchasedBefore = productIsPurchased(productId, productAction);
})

productForm.submit(function(event){
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
        productAction.html(
          "<a class='btn btn-link' href='/cart/' data-action='true'>In cart</a>" +
          "<button type='submit' class='btn btn-link mx-3' style='padding:0px' data-action='true'>Remove?</button>")
      } else{
          productAction.html(
            "<button type='submit' class='btn btn-success' data-action='true'>Add to cart</button>")

      }
      cartCounter = $(".navbar-cart-counter")
      cartCounter.text(formData.cart_count)

      var currentPath = window.location.href
      if (currentPath.indexOf('cart') !== -1){
        updateCart()
      }
    },
    error: function(error){
      update_messages([{"message": "Error.", "level": 'ERROR'}]);
      showPopUpBox("flashes");
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
        update_messages([{"message": "Error.", "level": 'ERROR'}]);
        showPopUpBox("flashes");
      }
    })
  }
})

// =========================
// CUSTOM FLASH-MESSAGES SETTINGS
// =========================

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
  $.each(messages, function (i, m) {
                  $("#popup-messages-content").append("<li><div class='alert alert-"+m.level+"''>"+m.message+"</div></li>");
              });
            }

// Extract form session flash messages that were sent from JS
  window.onload = function() {

      var message =  sessionStorage.getItem("message");
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
// ======================





// ======================
//  CUSTOM SLICK SETTINGS
// ======================

  $(document).ready(function(){
    $('.card-slider').slick({
      dots: false,
  infinite: true,
  speed: 300,
  slidesToShow: 5,
  slidesToScroll: 2,
  prevArrow:"<div class='slick-arrow-wrapper-left'>" +
  "<img class='a-left control-c prev slick-prev' src='static/images/circle-left.png'>" +
  "</div>",
  nextArrow:"<div class='slick-arrow-wrapper-right'>" +
  "<img class='a-right control-c next slick-next' src='static/images/circle-right.png'>"+
  "</div>",
  responsive: [
    {
      breakpoint: 1024,
      settings: {
        slidesToShow: 3,
        slidesToScroll: 3,
        infinite: true,
        dots: false
      }
    },
    {
      breakpoint: 600,
      settings: {
        slidesToShow: 2,
        slidesToScroll: 2
      }
    },
    {
      breakpoint: 480,
      settings: {
        slidesToShow: 1,
        slidesToScroll: 1
      }
    }
  ]
    });
  });

  // ======================
  //  CUSTOM SETTINGS: CLICKABLE CARDS
  // ======================

$(document).ready(function(){
  $(".clickable").click(function(){
    $this = $(this);
    var target = event.target;
    console.log(target)
    var action = $(target).attr('data-action');
    console.log('action')
    console.log(action)
    if (typeof action !== typeof undefined && action !== false){}else{
      var Url = $this.attr("data-url");
      window.location.href = Url;
    }
  });
});


// ======================
//  CUSTOM SETTINGS: GENRES DROPDOWN FROM NAVBAR
// ======================

$(document).ready(function(){
  var dropDown = $(".genres-dropdown")
  dropDown.click(function(event){
   $this = $(this)
   var method = "GET"
   var url = "/categories/data"
   var data = {}
   $.ajax({
    url: url,
    method: method,
    data: data,
    success: function(data){
      dropdownMenu = $(".genres-menu");
      dropdownMenu.html("");
      var txt = "<div><h6>Genres</h6></div><div class='columns'>";
      $.each(data.categories, function(i, c){
        txt += ("<a class='dropdown-item' href='" + c.url + "'>"+ c.title + "</a>")
      });
      txt += "</div";
      dropdownMenu.append(txt);
      },
      error: function(error){
      }
    });
  });
})
