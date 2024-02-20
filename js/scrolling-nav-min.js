!function(e){"use strict";e('a.js-scroll-trigger[href*="#"]:not([href="#"])').click(function(){if(location.pathname.replace(/^\//,"")==this.pathname.replace(/^\//,"")&&location.hostname==this.hostname){var t=e(this.hash);if((t=t.length?t:e("[name="+this.hash.slice(1)+"]")).length)return e("html, body").animate({scrollTop:t.offset().top-54},1e3,"easeInOutExpo"),!1}}),e(".js-scroll-trigger").click(function(){e(".navbar-collapse").collapse("hide")}),e("body").scrollspy({target:"#mainNav",offset:54})}(jQuery);

$(function() {
  $(window).scroll(function() {
    var x = $(window).scrollTop();

    if (x >= 120) {
      $("#header-logo").show();
      $('.navbar').addClass('scrolled');
    } else {
      $("#header-logo").hide();
      $('.navbar').removeClass('scrolled');
    }

  });

});

$(function () {
$('[data-toggle="popover"]').popover()
})
