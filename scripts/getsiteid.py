import sys

from hmnet import netdb

name = sys.argv[1]
s = netdb.Site(name)
print(name, s.siteid)
