odoo.define('hw_android.NfcReader', function (require) {
"use strict";

var BarcodeReader = require('point_of_sale.BarcodeReader');

BarcodeReader.include({
    connect_to_android_proxy: function () {
        if (this.env.pos.iot_device_proxies.android) {
            this.env.pos.iot_device_proxies.android.add_listener(function (barcode) {
                this.scan(barcode.value);
            });
        }
    },

    disconnect_from_android_proxy: function () {
        if (this.env.pos.iot_device_proxies.android) {
            this.env.pos.iot_device_proxies.android.remove_listener();
        }
    },
});

});
