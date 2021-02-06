$( "tr.table" ).click(function() {
    if ($(this).hasClass("selected")) {
        $(this).removeClass("selected");
    }
    else {
        $('table > tbody > tr').each(function(i, tr) { 
            $(tr).removeClass("selected");
        });
        $(this).addClass("selected");
    };
});

$('.table.action').click(function() {
    table = $('table > tbody > tr.selected');
    table_value = $(table).attr("value")
    if (typeof table_value === "undefined") {
        console.log("NO ROW SELECTED")
        $(".errors").append( "Select a row first!" );
    }
    else if ($(this).attr("meth") == "post") {
        $.ajax({
            url: $(this).attr("href") + table_value,
            data: {},
            type: 'POST',
            success: function(response) {
                $(table).remove();
            },
            error: function(error) {
                console.log(error);
            }
        });
    }
    else {
        console.log("NAV")
        window.location.replace($(this).attr("href") + table_value);
    }
});
