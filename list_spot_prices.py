#!/usr/bin/env python

__author__ = 'bryan'

from beaker import *
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import os
import boto
import boto.ec2
from spot import *

TMPDIR=os.getenv("TMPDIR")

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': '%s/cache/data.list_spot_prices' % (TMPDIR),
    'cache.lock_dir': '%s/cache/lock.list_spot_prices' % (TMPDIR)
}

cache = CacheManager(**parse_cache_config_options(cache_opts))

def price_history(conn):
    prices = conn.get_spot_price_history(product_description='Linux/UNIX')
    prices = sorted(prices, key=lambda p: p.timestamp)
    by_type = {}
    for f in prices:
        by_type[f.instance_type, f.availability_zone] = []
    for f in prices:
        by_type[f.instance_type, f.availability_zone] += [ f ]
    return by_type

class Price:
    def __init__(self, arch, zone, last, per_ecore_average, num_cores):
        self.arch = arch
        self.zone = zone
        self.last = last
        self.per_ecore_average = per_ecore_average
        self.num_cores = num_cores

@cache.cache('spot_listing', expire=3601)
def price_info(conn):
    prices = price_history(conn)
    spot = SpotCPU()
    price_list = []
    for f in prices.keys():
        price_per_core = spot.GetPerECorePrice(
            f[0],
            sum(p.price for p in prices[f])/len(prices[f]))
        price_list.append(Price(f[0], f[1], prices[f][0].price,
                                    price_per_core,
                                    spot.GetCpuCount(f[0])))
    price_list = sorted(price_list, key=lambda p: p.per_ecore_average)
    return price_list

def main():
   ec2 = boto.connect_ec2()
   print "zone,last,num_cores,ecore_average,curr" 
   for ri in price_info(ec2):
       print "%s,%s,%1.3f,%s,%-.3f,%-.3f "  % ( 
               ri.zone, 
               ri.arch, 
               ri.last, 
               ri.num_cores,      
               ri.per_ecore_average,              
               (ri.num_cores *  ri.per_ecore_average)
               )
   
if __name__ == '__main__':
   main() 
