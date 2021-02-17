let vh = window.innerHeight * 0.01;
document.documentElement.style.setProperty('--vh', `${vh}px`);

window.addEventListener('resize', () => {
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
});

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

$('.viewable').click(function() {
    placeholder = $('.category.placeholder')
    placeholder.html($(this).html());
    placeholder.addClass("loaded " + $(this).attr('class').split(' ')[1]);
    placeholder.find('.details').addClass('c back');
    placeholder.animate({'height': '92vh'}, 300);
    placeholder.animate({'height': '90vh'}, 150);
});

$('body').on('click','.c.back',function() {
    placeholder = $('.category.placeholder')
    placeholder.animate({'height': '91vh'}, 100, function() {
        placeholder.animate({'height': '0vh'}, 400, function() {
            placeholder.attr('class', 'category placeholder');
            placeholder.html('');
        });
    });
});

$('body').on('click','.dish.item',function() {
    html = $(this).html();
    type = $('.category.placeholder').attr('class').split(' ')[3];

    placeholder_image = $('.dish.placeholder.image')
    placeholder_image.addClass(type);
    placeholder_image.append($(this).find('img:first').clone());
    placeholder_image.animate({'height': '40vh'}, 500);

    placeholder = $('.dish.placeholder.data')
    placeholder.addClass(type);
    placeholder.append($(this).find('.data').clone());
    placeholder.append($(this).find('.expanded').clone());
    placeholder.animate({'height': '65vh'}, 600);
});

$('body').on('click','.d.back',function() {
    placeholder_image = $('.dish.placeholder.image')
    placeholder_image.animate({'height': '0vh'}, 600, function() {
        placeholder_image.attr('class', 'dish placeholder image');
        placeholder_image.find('img:nth-child(2)').remove();
    });

    placeholder = $('.dish.placeholder.data')
    placeholder.animate({'height': '0vh'}, 600, function() {
        placeholder.attr('class', 'dish placeholder data');
        placeholder.html('');
    });
});