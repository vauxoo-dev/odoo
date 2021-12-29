odoo.define('hw_android.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var DeviceProxy = require('iot.DeviceProxy');

    models.load_models([{
        model: 'iot.device',
        fields: ['iot_ip', 'iot_id', 'identifier', 'type', 'manual_measurement'],
        domain: function(self) {
            var device_ids = self.config.iot_device_ids;
            return [['id', 'in', device_ids]];
        },
        loaded: function(self, iot_devices) {
            _.each(iot_devices, function(iot_device) {
                switch (iot_device.type) {
                    case 'android':
                        self.iot_device_proxies[iot_device.type] = new DeviceProxy(
                            self, { iot_ip: iot_device.iot_ip, identifier: iot_device.identifier});
                        break;
                }
            });
        },
    }]);

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        connect_to_proxy: function () {
            var result = _super_order.connect_to_proxy.apply(this, arguments);
            if (this.config.iface_android_via_proxy) {
                this.barcode_reader.connect_to_android_proxy();
            }
            return result;
        },
    });

});
