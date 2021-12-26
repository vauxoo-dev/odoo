# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from usb import core

from odoo.addons.hw_drivers.interface import Interface


class AndroidNFCInterface(Interface):
    connection_type = 'android'

    def get_devices(self):
        """TODO:
        """
        nfc_devices = {}
        devs = core.find(find_all=True)
        # Here instead of the core.fin from usb lib, we need retrieve all devices already register by http hook
        # devs = from/file/var/obj/memory
        cpt = 2
        for dev in devs:
            identifier = "nfc_%04x:%04x" % (dev.idVendor, dev.idProduct)
            if identifier in nfc_devices:
                identifier += '_%s' % cpt
                cpt += 1
            nfc_devices[identifier] = dev
        return nfc_devices
