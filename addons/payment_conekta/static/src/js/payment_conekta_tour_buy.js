odoo.define('payment_conekta.tour', function (require) {
'use strict';

var Tour = require('web_tour.tour');
var base = require('web_editor.base');

Tour.register('shop_buy_prod_conekta', {
    url: '/shop',
    test: true,
    wait_for: base.ready()
},
    [
        {
            content:     "select ipod",
            trigger:   '.oe_product_cart a:contains("iPod")',
        },
        {
            content:     "click on add to cart",
            trigger:   '#product_detail form[action^="/shop/cart/update"] .btn',
        },
        {
            content:     "go to checkout",
            trigger:   'a[href="/shop/checkout"]',
        },
        {
            content:     "test without input error",
            trigger:   'form[action="/shop/confirm_order"] .btn:contains("Confirm")',
            onload: function (tour) {
                if ($("input[name='name']").val() === "")
                    $("input[name='name']").val("website_sale-test-shoptest");
                if ($("input[name='email']").val() === "")
                    $("input[name='email']").val("website_sale_test_shoptest@websitesaletest.odoo.com");
                $("input[name='phone']").val("123123123");
                $("input[name='street2']").val("123");
                $("input[name='city']").val("123");
                $("input[name='zip']").val("123");
                $("select[name='country_id']").val("21");
            },
        },
        {
            content:     "select payment",
            trigger:   '#payment_method label:has(img[title="Conekta"]) input',
        },
        {
            content:     "Pay Now",
            waitFor:   '#payment_method label:has(input:checked):has(img[title="Conekta"])',
            trigger:   '.oe_sale_acquirer_button .btn[name="conekta"]:visible',
            onload: function(tour){
                $('input[data-conekta="card[name]"]').val('payment_conekta-test');
                $('input[data-conekta="card[number]"]').val('4242424242424242');
                $('input[data-conekta="card[cvc]"]').val('123');
                $('input[data-conekta="card[exp_month]"]').val('10');
                $('input[data-conekta="card[exp_year]"]').val('2019');
            },
        },
        {
            content:     "finish",
            waitFor:   '.oe_website_sale:contains("Thank you for your order")',
        }
    ]
);

});

