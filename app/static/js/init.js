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
var set = function(item, img, price, new_value) {
    CART[item]['img'] = img;
    CART[item]['price'] = price;
    CART[item]['count'] = new_value;

    let count = 0;
    let total = 0;
    $('.cart .full').html('');
    $.each(CART, function(i, element) {
        count += element['count'];
        total += element['price'] * element['count'];
        let cart_item = '<div dish="'+i+'" class="item"><h5 class="nr">x'+element["count"]+'</h5><img src="'+element["img"]+'"><p>'+i+'</p><h5>'+element["price"]+'0</h5><img class="minus" src="/static/img/icons/minus.png"></div>';
        $('.cart .full').append(cart_item);
    });

    $(".total").text(total + ".00 LEI");

    $('.cart').animate({'height': '4em'}, 300);
    $('.categories .category:last-child').find('.details').addClass("cart_padder");
};

$('body').on('click','.cart:not(.extended)',function() {
    $(this).addClass("extended");
    $(this).animate({'height': '100%'}, 300);
});

$('body').on('click','.cart .hide',function(event) {
    event.stopPropagation();
    $('.cart').removeClass("extended");
    $('.cart').animate({'height': '4em'}, 300);
});

$('body').on('click','.add',function(event) {
    event.stopPropagation();

    dish = $(this).attr('dish');
    price = $(this).attr('price');
    img = $(this).attr('img');
    if (CART[dish] == undefined) {
        CartDisplay = true;
        CART[dish] = {};
        set(dish, img, price, 1);
    }
    else {
        set(dish, img, price, CART[dish]['count'] + 1);
    }
    console.log("ADDED", CART);
});

$('body').on('click','.minus',function() {
    item = $(this).parent();
    dish = item.attr('dish')
    CART[dish]['count'] -= 1;
    if (CART[dish]['count'] == 0) {
        delete CART[dish];
        item.fadeOut();
    }
    else {
        item.find('.nr').text('x' + CART[dish]['count']);
    }

    if (Object.keys(CART).length === 0) {
        $('.cart').removeClass("extended");
        $('.cart').animate({'height': '0em'}, 300);
        $('.categories .category:last-child').find('.details').removeClass("cart_padder");
    }
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
    placeholder.append($(this).find('.open').clone());
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