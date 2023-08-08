/** @odoo-module **/

import { WebsiteSale } from "@website_sale/js/website_sale";

WebsiteSale.include({
    events: Object.assign({}, WebsiteSale.prototype.events, {
        "change select[name='state_id']": "_onChangeState",
        "change select[name='city_id']": "_onChangeCity",
    }),
    _changeState: function () {
        if (!$("#state_id").val()) {
            return;
        }
        this._rpc({
            route: "/shop/state_infos/" + $("#state_id").val(),
            params: {
                mode: $("#country_id").attr("mode"),
            },
        }).then(data => {
            // populate cities and display
            let selectCities = $("select[name='city_id']");
            let selectDistricts = $("select[name='l10n_pe_district']");
            if (data.cities.length) {
                selectCities.html("");
                selectCities.append($("<option>").text("City..."));
                $.each(data.cities, function (c) {
                    let opt = $("<option>").text(data.cities[c][1]).attr("value", data.cities[c][0]).attr("data-code", data.cities[c][2]);
                    selectCities.append(opt);
                });
                selectCities.parent("div").show();
            } else {
                selectCities.val("").parent("div").hide();
            }
            selectDistricts.val("").parent("div").hide();
        });
    },
    _changeCity: function () {
        if (!$("#city_id").val()) {
            return;
        }
        this._rpc({
            route: "/shop/city_infos/" + $("#city_id").val(),
            params: {
                mode: $("#country_id").attr("mode"),
            },
        }).then(data => {
            // populate districts and display
            let selectDistricts = $("select[name='l10n_pe_district']");
            if (data.districts.length) {
                selectDistricts.html("");
                $.each(data.districts, function (d) {
                    let opt = $("<option>").text(data.districts[d][1]).attr("value", data.districts[d][0]).attr("data-code", data.districts[d][2]);
                    selectDistricts.append(opt);
                });
                selectDistricts.parent("div").show();
            } else {
                selectDistricts.val("").parent("div").hide();
            }
        });
    },
    _onChangeState: function (ev) {
        if (!this.$(".checkout_autoformat").length) {
            return;
        }
        this._changeState();
    },
    _onChangeCity: function (ev) {
        if (!this.$(".checkout_autoformat").length) {
            return;
        }
        this._changeCity();
        let selectedValue = $(ev.currentTarget).find("option:selected").text();
        let cityBlock = $(".div_city")
        cityBlock.find("input").val("\n " + selectedValue);
    },
    _onChangeCountry: function (ev) {
        this._super(...arguments);
        let selectedCountry = $(ev.currentTarget).find("option:selected").attr("code");
        let cityBlock = $(".div_city")

        if (selectedCountry == "PE"){
            cityBlock.addClass("d-none");
        }
        else if (selectedCountry != "PE"){
            cityBlock.find("input").val("");
            cityBlock.removeClass("d-none");
            let selectCities = $("select[name='city_id']");
            let selectDistricts = $("select[name='l10n_pe_district']");
            selectCities.val("").parent("div").hide();
            selectDistricts.val("").parent("div").hide();
        }
    },
});
