odoo.define('hw_android.NfcReader', function (require) {
"use strict";

var BarcodeReader = require('point_of_sale.BarcodeReader');

BarcodeReader.include({
    connect_to_android_proxy: function () {
        var self = this;
        if (this.pos.iot_device_proxies.android) {
            this.pos.iot_device_proxies.android.add_listener(function (barcode) {
                self.scan(barcode.value);
            });
        }
    },

    disconnect_from_android_proxy: function () {
        if (this.pos.iot_device_proxies.android) {
            this.pos.iot_device_proxies.android.remove_listener();
        }
    },
});

});
