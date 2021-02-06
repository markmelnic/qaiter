$("table").on("click", "tr.table", function() { 
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
    row = $('table > tbody > tr.selected');
    row_value = $(row).attr("value")
    url = $(this).attr("href") + row_value
    if (typeof row_value === "undefined") {
        $(".errors").append("Select a row first!");
    }
    else if ($(this).attr("meth") == "post") {
        $.ajax({
            url: url,
            data: {},
            type: 'POST',
            success: function(response) {
                table = row.closest("table");
                $(row).remove();
                if (url.includes("toggle")) {
                    $(row).removeClass("selected");
                    if ($(table).hasClass("active")) {
                        $("table.disabled").append(row);
                    }
                    else if ($(table).hasClass("disabled")) {
                        $("table.active").append(row);
                    }
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    }
    else {
        window.location.replace(url);
    }
});
