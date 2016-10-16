$(document).ready(function(){
     $(window).scroll(function () {
            if ($(this).scrollTop() > 1080) {
                $('#back-to-top').show();
            } else {
                $('#back-to-top').hide();
            }
        });
        // scroll body to 0px on click
        $('#back-to-top').click(function () {
            $('body,html').animate({
                scrollTop: 0
            }, 800);
            return false;
        });

});
