$( "tr.table" ).click(function(e) {
    e.preventDefault();
    console.log($(this).attr("value"));

    if ($(this).hasClass("selected")) {
        $(this).removeClass("selected");
    }
    else {
        $('table > tbody  > tr').each(function(index, tr) { 
            $(tr).removeClass("selected");
        });
        $(this).addClass("selected");
    };
});

$('tr').click(function(e){
    e.preventDefault();
    $('tr').removeClass('highlight'); // removes all highlights from tr's
    $(this).addClass('highlight'); // adds the highlight to this row
});