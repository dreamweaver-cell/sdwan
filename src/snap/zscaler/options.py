locations_ssl_cltcon_noenforce = {"id": 59310118, "name": "Locations_SSL_CltCon_NoEnforce"}
locations_ssl = {"id": 59310120, "name": "Locations_SSL"}
sdwan_dns_locations = {"id": 57372364, "name": "SDWAN-DNS-LOCATIONS"}
sdwan_icmp_allow = {"id": 60214508, "name": "SDWAN-ICMP-ALLOW"}
lib_guest_access_locations = {"id": 42956511, "name": "LIB-Guest-Access-locations"}
locations_nossl_cltcon_noenforce = {"id": 59310116, "name": "Locations_NoSSL_CltCon_NoEnforce"}
locations_nossl = {"id": 59310117, "name": "Locations_NoSSL"}

ZS_SDWAN_OPTIONS = {
    "other": [
        locations_ssl_cltcon_noenforce, locations_ssl, sdwan_dns_locations, sdwan_icmp_allow
    ],
    "hm-wifi-guest": [
        lib_guest_access_locations, locations_nossl, locations_nossl_cltcon_noenforce,
        sdwan_icmp_allow
    ]
}
