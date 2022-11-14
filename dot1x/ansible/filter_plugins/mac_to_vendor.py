from mac_vendor_lookup import MacLookup


class FilterModule(object):
    ''' map MAC to vendor '''

    def filters(self):
        return {'mac_to_vendor': self.mac_to_vendor}

    def mac_to_vendor(self, mac):
        try:
            return MacLookup().lookup(mac)
        except Exception:
            return 'NA'
