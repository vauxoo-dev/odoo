/** @odoo-module **/
import { WebsiteSale } from "@website_sale/js/website_sale";

WebsiteSale.include({
    events: Object.assign({}, WebsiteSale.prototype.events, {
        "change select[name='state_id']": "_onChangeState",
        "change select[name='city_id']": "_onChangeCity",
    }),
    start: function () {
        this.selectCities = document.querySelector("select[name='city_id']");
        this.selectDistricts = document.querySelector("select[name='l10n_pe_district']");
        this.cityBlock = document.querySelector(".div_city");
        this.autoFormat = document.querySelector(".checkout_autoformat");
        this.selectedState = document.querySelector("select[name='state_id']");
        return this._super.apply(this, arguments);
    },
    _changeState: function () {
        if (!document.getElementById("state_id").value) {
            return;
        }
        this._rpc({
            route: "/shop/state_infos/" + document.getElementById("state_id").value,
        }).then(data => {
            // populate cities and display
            if (data.cities.length) {
                this.selectCities.innerHTML = "";
                let option = document.createElement("option");
                option.textContent = "City...";
                this.selectCities.appendChild(option);
                data.cities.forEach(city => {
                    let opt = document.createElement("option");
                    opt.textContent = city[1];
                    opt.value = city[0];
                    opt.setAttribute("data-code", city[2]);
                    this.selectCities.appendChild(opt);
                });
                this.selectCities.parentElement.style.display = "block";
            } else {
                this.selectCities.value = "";
                this.selectCities.parentElement.style.display = "none";
            }
            this.selectDistricts.value = "";
            this.selectDistricts.parentElement.style.display = "none";
        });
    },
    _changeCity: function () {
        if (!document.getElementById("city_id").value) {
            return;
        }
        this._rpc({
            route: "/shop/city_infos/" + document.getElementById("city_id").value,
        }).then(data => {
            // populate districts and display
            if (data.districts.length) {
                this.selectDistricts.innerHTML = "";
                data.districts.forEach(district => {
                    let opt = document.createElement("option");
                    opt.textContent = district[1];
                    opt.value = district[0];
                    opt.setAttribute("data-code", district[2]);
                    this.selectDistricts.appendChild(opt);
                });
                this.selectDistricts.parentElement.style.display = "block";
            } else {
                this.selectDistricts.value = "";
                this.selectDistricts.parentElement.style.display = "none";
            }
        });
    },
    _onChangeState: function (ev) {
        if (!this.autoFormat.length) {
            return;
        }
        this._changeState();
    },
    _onChangeCity: function (ev) {
        if (!this.autoFormat.length) {
            return;
        }
        this._changeCity();
    },
    _onChangeCountry: function (ev) {
        this._super(...arguments);

        // si el div de state se muestra hacer trigger del change state

        // Create a new 'change' event en JS
        // var event = new Event('change');
        // this.selectedState.dispatchEvent(event);

        // jquery
        $(this.selectedState).change();

        let selectedCountry = ev.currentTarget.options[ev.currentTarget.selectedIndex].getAttribute("code");

        if (selectedCountry == "PE") {
            this.cityBlock.classList.add("d-none");
        } else if (selectedCountry != "PE") {
            this.cityBlock.querySelectorAll("input").forEach(input => {
                input.value = "";
            });
            this.cityBlock.classList.remove("d-none");
            this.selectCities.value = "";
            this.selectCities.parentElement.style.display = "none";
            this.selectDistricts.value = "";
            this.selectDistricts.parentElement.style.display = "none";
        }
    },
});
