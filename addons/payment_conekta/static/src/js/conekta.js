odoo.define("payment_conekta.payment", function (require) {
    "use strict";


    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var Dialog = require("web.Dialog");
    var Widget = require("web.Widget");
    var rpc = require("web.rpc");
    var PaymentForm = require('payment.payment_form');
    var _t = core._t;


    if(!$('#o_payment_form_pay').length) {
        return $.Deferred().reject("DOM doesn't contain '#o_payment_form_pay'");
    }

    var $payment = $("#payment_method"),
        so_id = $("input[name='sale_order']").val(),
        $form = $(".o_payment_form"),
        $button = $('#o_payment_form_pay');
        if (so_id) {
            so_id = parseInt(so_id);
        }
    $button.attr('disabled', true);
    $payment.on("change", '.o_payment_form', function (ev) {
        var empty_inputs = $(this).find('input[data-conekta^="card"]').filter(function() {return $(this).val() == ''});
        if (!empty_inputs.length == 0) {
            return false;
        }
        var $acquirer_radio = $('input[type="radio"]:checked'),
            acquirer_id = $acquirer_radio.data('acquirer-id');
        Conekta.token.create($form, conektaSuccessResponseHandler, conektaErrorResponseHandler);
        $button.attr('disabled', false);
        return false;
    });

    var conektaSuccessResponseHandler = function(token) {
        var $acquirer_radio = $form.find('input[type="radio"]:checked'),
            acquirer_id = $acquirer_radio.data('acquirer-id'),
            acquirer_form = $form.find('#o_payment_add_token_acq_' + acquirer_id),
            partner_id = $('input[name=partner_id]').val(),
            cc_number = $('input[name=cc_number]').val();
            acquirer_form.append($("<input type='hidden' name='token_id'>").val(token.id));
            ajax.jsonRpc('/payment/conekta/s2s/create_json_3ds', 'call', {
                'token': token.id,
                'token_id': token.id,
                'acquirer_id': acquirer_id,
                'partner_id': partner_id,
                'cc_number': cc_number}).then(function(response) {
                if (response.result == true) {
                    acquirer_form.append($("<input type='hidden' name='payment_token_id'>").val(response.id));
                } else {
                    $form.find(".card-errors").text(response).addClass("alert alert-danger");
                    $form.find("button").prop("disabled", false).button('reset');
                }
            });
    };

    var conektaErrorResponseHandler = function(response) {
        $form.find(".card-errors").text(response.message);
        $form.find("button").prop("disabled", false);
    };
    $form.on('click', "input[name='pm_id']", function (ev) {
        var current_acq = $(ev.target).data('provider');
        if (current_acq != 'conekta') {
            $button.attr('disabled', false);
        } else {
            $button.attr('disabled', true);
        }
    });
});
