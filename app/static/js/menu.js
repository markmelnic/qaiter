$( "#add-ingredient" ).click(function() {
    var ingredient = $('#name-ingredient-input').val();
    var quantity = $('#qty-ingredient-input').val();
    var qty_type = $('#qty-type').val();

    $("#ingredients-list").append('<li>' + ingredient + quantity + qty_type + '</li>');
    var value = $('#ingredients').val();
    value = value + ingredient + "-" + quantity + "-" + qty_type + "|"
    $("#ingredients").attr("value",value);

    $('#name-ingredient-input').val('');
    $('#qty-ingredient-input').val('');
});
