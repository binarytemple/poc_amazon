#!/usr/bin/env python

__author__ = 'bryan'
import boto

from beaker import *
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options



#cache_opts = {
#    'cache.type': 'file',
#    'cache.data_dir': '/tmp/cache/data.list_all_instances',
#    'cache.lock_dir': '/tmp/cache/lock.list_all_instances'
#}

#cache = CacheManager(**parse_cache_config_options(cache_opts))

#ec2 = boto.connect_ec2()

#@cache.cache('hit_me_again', expire=3600)
#def region_instances_list():
#    def safeTags(tags):
#        try:
#            return map(lambda x: "%s:%s" %  (x[0],x[1]),  tags.iteritems() ) 
#        except:
#            return "error"
#
#    for r in ec2.get_all_regions():
#        ret = []
#        rcon = r.connect()
#        for rinst in rcon.get_all_instances():
#            i = rinst.instances[0]
#            ret.append( [
#                r.name, i.image_id, i.state, i.persistent,\
#                i.dns_name,i.ip_address,\
#                i.instance_type, safeTags(i.tags)])
#        return ret
#
#print "Region Name, image_id, image_state, persistent,dns_name,ip_address,type,tags"
#
#for ri in region_instances_list():
#    print "%s,%s,%s,%s,%s,%s,%s,%s"  % ( ri[0],ri[1],ri[2],ri[3],ri[4],ri[5],ri[6],ri[7])



import boto
import boto.ec2
from spot import *

def GetPriceHistory(conn):
    prices = conn.get_spot_price_history(product_description='Linux/UNIX')
    prices = sorted(prices, key=lambda p: p.timestamp)
    by_type = {}
    for f in prices:
        by_type[f.instance_type, f.availability_zone] = []
    for f in prices:
        by_type[f.instance_type, f.availability_zone] += [ f ]
    return by_type

class PriceInfo:
    def __init__(self, arch, zone, last, per_ecore_average, num_cores):
        self.arch = arch
        self.zone = zone
        self.last = last
        self.per_ecore_average = per_ecore_average
        self.num_cores = num_cores

def GetPriceInfo(conn):
    prices = GetPriceHistory(conn)
    spot = SpotCPU()
    price_list = []
    for f in prices.keys():
        price_per_core = spot.GetPerECorePrice(
            f[0],
            sum(p.price for p in prices[f])/len(prices[f]))
        price_list.append(PriceInfo(f[0], f[1], prices[f][0].price,
                                    price_per_core,
                                    spot.GetCpuCount(f[0])))
    price_list = sorted(price_list, key=lambda p: p.per_ecore_average)
    return price_list


def main():
   ec2 = boto.connect_ec2()
   print "arch,last,num_cores,ecore_average,curr" 
   for ri in GetPriceInfo(ec2):
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
