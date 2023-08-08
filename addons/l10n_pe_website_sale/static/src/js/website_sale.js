/** @odoo-module **/

import { WebsiteSale } from "@website_sale/js/website_sale";

WebsiteSale.include({
    events: Object.assign({}, WebsiteSale.prototype.events, {
        "change select[name='state_id']": "_onChangeState",
        "change select[name='city_id']": "_onChangeCity",
    }),
    start: function () {
        this.selectCities = $("select[name='city_id']");
        this.selectDistricts = $("select[name='l10n_pe_district']");
        this.cityBlock = $(".div_city");
        return this._super.apply(this, arguments);
    },
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
            if (data.cities.length) {
                this.selectCities.html("");
                this.selectCities.append($("<option>").text("City..."));
                $.each(data.cities, (c) => {
                    let opt = $("<option>").text(data.cities[c][1]).attr("value", data.cities[c][0]).attr("data-code", data.cities[c][2]);
                    this.selectCities.append(opt);
                });
                this.selectCities.parent("div").show();
            } else {
                this.selectCities.val("").parent("div").hide();
            }
            this.selectDistricts.val("").parent("div").hide();
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
            if (data.districts.length) {
                this.selectDistricts.html("");
                $.each(data.districts, (d) => {
                    let opt = $("<option>").text(data.districts[d][1]).attr("value", data.districts[d][0]).attr("data-code", data.districts[d][2]);
                    this.selectDistricts.append(opt);
                });
                this.selectDistricts.parent("div").show();
            } else {
                this.selectDistricts.val("").parent("div").hide();
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
    },
    _onChangeCountry: function (ev) {
        this._super(...arguments);
        let selectedCountry = $(ev.currentTarget).find("option:selected").attr("code");

        if (selectedCountry == "PE"){
            this.cityBlock.addClass("d-none");
        }
        else if (selectedCountry != "PE"){
            this.cityBlock.find("input").val("");
            this.cityBlock.removeClass("d-none");
            this.selectCities.val("").parent("div").hide();
            this.selectDistricts.val("").parent("div").hide();
        }
    },
});
