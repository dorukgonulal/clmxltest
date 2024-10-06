$(document).ready(function(){
    $(window).scroll(function(){
        var scroll = $(window).scrollTop();
        if (scroll > 50) {
          $(".navbar").css("background" , "black");
          $(".navbar").css("padding", "2.5vh")
          $(".navbar").css("transition", ".4s")
        }
  
        else{
            $(".navbar").css("background" , "transparent");
            $(".navbar").css("padding", "4vh")
            $(".navbar").css("transition", ".4s")
        }
    })
  })