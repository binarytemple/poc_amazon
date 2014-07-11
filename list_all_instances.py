#!/usr/bin/env python

__author__ = 'bryan'
import boto

from beaker import *
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options



cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': '/tmp/cache/data.list_all_instances',
    'cache.lock_dir': '/tmp/cache/lock.list_all_instances'
}

cache = CacheManager(**parse_cache_config_options(cache_opts))

ec2 = boto.connect_ec2()

@cache.cache('hit_me_again', expire=3600)
def region_instances_list():

    def safeTags(tags):
        try:
            return tags.items()
        except:
            return "error"

    for r in ec2.get_all_regions():
        ret = []
        rcon = r.connect()
        for rinst in rcon.get_all_instances():
            i = rinst.instances[0]
            ret.append( [
                r.name, i.image_id, i.state, i.persistent,\
                i.dns_name,i.ip_address,\
                i.instance_type, safeTags(i.tags)])
        return ret

print "Region Name, image_id, image_state, persistent,dns_name,ip_address,type,tags"

for ri in region_instances_list():
    print "%s,%s,%s,%s,%s,%s,%s,%s"  % ( ri[0],ri[1],ri[2],ri[3],ri[4],ri[5],ri[6],ri[7])
