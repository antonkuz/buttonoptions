jQuery(function ($) {
    //submit the form only if it's complete
    $('#survey').submit(function (e) {
        //check radiobuttons
        if (!$("input[name='a']:checked").val()) {
            e.preventDefault();
        }
        if (!$("input[name='b']:checked").val()) {
            e.preventDefault();
        }
        //check free response
        if ($(".fr1").val()=='') {
            e.preventDefault();
        }
    })
})