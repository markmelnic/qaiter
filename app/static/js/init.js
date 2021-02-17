// responsive vh
var vh = window.innerHeight * 0.01;
document.documentElement.style.setProperty('--vh', `${vh}px`);

window.addEventListener('resize', () => {
    var vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
});

// app init
cats_nr = $('.categories').children('.category').length - 1;
$('.categories').children('.category').each(function(i) {
    if (i % 2 == 0) {
        if (i == 1) {
            $(this).addClass("stype");
        }
        else {
            $(this).addClass("utype");
        }

        if (i == 0) {
            $(this).find(">:first-child").addClass("stype");
        }
        else {
            $(this).find(">:first-child").addClass("etype");
        }
    }
    else if (i % 2 == 1) {
        if (i == 1) {
            $(this).addClass("stype");
        }
        else {
            $(this).addClass("etype");
        }

        if (i == 0) {
            $(this).find(">:first-child").addClass("stype");
        }
        else {
            $(this).find(">:first-child").addClass("utype");
        }
    }
});

// cart handlers
var CART = {};
var CartDisplay = false;
var set = function(item, price, new_value) {
    CART[item]['price'] = price;
    CART[item]['count'] = new_value;

    count = 0;
    total = 0;
    $.each(CART, function(i, element) {
        count += element['count'];
        total += element['price'] * element['count'];
    });

    $(".count").text("x" + count);
    $(".total").text("MDL " + total + ".00");

    $('.cart').animate({'height': '3em'}, 150);

    $('.categories .category:last-child>div>div').addClass("cart_padder");
    $('.category.placeholder').addClass("cart_padder");

    //$('.categories .category:last-child>div>div').animate({'padding-bottom': '3em'}, 150);
    //$('.category.placeholder').animate({'padding-bottom': '3em'}, 150);
};

$('body').on('click','.add',function(event) {
    event.stopPropagation();

    dish = $(this).attr('dish');
    price = $(this).attr('price');
    if (CART[dish] == undefined) {
        CartDisplay = true;
        CART[dish] = {};
        set(dish, price, 1);
    }
    else {
        set(dish, price, CART[dish]['count'] + 1);
    }
    console.log("ADDED", CART);
});

$('body').on('click','.remove',function() {
    dish = $(this).attr('dish');
    price = $(this).attr('price');
    set(dish, price, CART[dish]['count'] - 1);
    console.log("REMOVED", CART);
});

// animations, loaders, etc.
$('.viewable').click(function() {
    placeholder = $('.category.placeholder')
    placeholder.html($(this).html());
    if (CartDisplay) {
        placeholder.addClass("cart_padder");
    }
    placeholder.addClass("loaded " + $(this).attr('class').split(' ')[1]);
    placeholder.find('.details').addClass('c back');
    placeholder.animate({'height': '82%'}, 300);
    placeholder.animate({'height': '80%'}, 150);
});

$('body').on('click','.c.back',function() {
    placeholder = $('.category.placeholder')
    placeholder.animate({'height': '81%'}, 100, function() {
        placeholder.animate({'height': '0%'}, 400, function() {
            placeholder.attr('class', 'category placeholder');
            placeholder.html('');
        });
    });
});

function getType(item) {
    if (item.hasClass('stype')) {
        type = "stype";
    }
    else if (item.hasClass('etype')) {
        type = "etype";
    }
    else if (item.hasClass('utype')) {
        type = "utype";
    }
    return type;
};

$('body').on('click','.dish.item',function() {
    html = $(this).html();
    type = getType($('.category.placeholder'));

    placeholder_image = $('.dish.placeholder.image')
    placeholder_image.addClass(type);
    placeholder_image.append($(this).find('img:first').clone());
    placeholder_image.animate({'height': '40%'}, 500);

    placeholder = $('.dish.placeholder.data')
    placeholder.addClass(type);
    placeholder.append($(this).find('.data').clone());
    placeholder.append($(this).find('.expanded').clone());
    placeholder.animate({'height': '65%'}, 600);
});

$('body').on('click','.d.back',function() {
    placeholder_image = $('.dish.placeholder.image')
    placeholder_image.animate({'height': '0%'}, 600, function() {
        placeholder_image.attr('class', 'dish placeholder image');
        placeholder_image.find('img:nth-child(2)').remove();
    });

    placeholder = $('.dish.placeholder.data')
    placeholder.animate({'height': '0%'}, 600, function() {
        placeholder.attr('class', 'dish placeholder data');
        placeholder.html('');
    });
});