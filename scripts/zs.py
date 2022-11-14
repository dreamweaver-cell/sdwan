from snap.zscaler import ZS

zs = ZS()

loc = zs.locations.get_location(location_name="sesthit1lab")
print(loc)
