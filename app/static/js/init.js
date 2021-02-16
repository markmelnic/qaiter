let vh = window.innerHeight * 0.01;
document.documentElement.style.setProperty('--vh', `${vh}px`);

window.addEventListener('resize', () => {
    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
});

cats_nr = $('.categories').children('.category').length - 1;
$('.categories').children('.category').each(function(i) {
    if (i % 2 == 0) {
        $(this).addClass("utype");
        if (i == cats_nr) {
            $(this).find(">:first-child").addClass("stype");
        }
        else {
            $(this).find(">:first-child").addClass("etype");
        }
    }
    else if (i % 2 == 1) {
        $(this).addClass("etype");
        if (i == cats_nr) {
            $(this).find(">:first-child").addClass("stype");
        }
        else {
            $(this).find(">:first-child").addClass("utype");
        }
    }
});

$('.viewable').click(function() {
    type = $(this).attr('class').split(' ')[1]
    html = $(this).html();

    placeholder = $('.category.placeholder')
    placeholder.html(html);
    placeholder.addClass("loaded " + type);
    placeholder.animate({'height': '92vh'}, 300);
    placeholder.animate({'height': '90vh'}, 150);
});

$('body').on('click','img.back',function() {
    placeholder = $('.category.placeholder')
    placeholder.animate({'height': '91vh'}, 100, function() {
        placeholder.animate({'height': '0vh'}, 400, function() {
            placeholder.attr('class', 'category placeholder');
            placeholder.html('');
        });
    });
});