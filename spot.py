# Copyright 2014
# Author: Christopher Van Arsdale

#Copyright (c) 2014, Christopher Van Arsdale
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification,
#are permitted provided that the following conditions are met:
#
#* Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#
#* Redistributions in binary form must reproduce the above copyright notice, this
#  list of conditions and the following disclaimer in the documentation and/or
#  other materials provided with the distribution.
#
#* Neither the name of the {organization} nor the names of its
#  contributors may be used to endorse or promote products derived from
#  this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
#ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



class SpotCPU:
    def __init__(self):
        self.expected_cpu_count = {
            "t1.micro": 0.1,
            "m3.medium": 3,
            "m3.large": 6.5,
            "m3.xlarge": 13,
            "m3.2xlarge": 26,
            "m1.small": 1,
            "m1.medium": 2,
            "m1.large": 4,
            "m1.xlarge": 8,
            "c3.large": 7,
            "c3.xlarge": 14,
            "c3.2xlarge": 28,
            "c3.4xlarge": 55,
            "c3.8xlarge": 108,
            "c1.medium": 5,
            "c1.xlarge": 20,
            "cc2.8xlarge": 88,
            "g2.2xlarge": 26,
            "cg1.4xlarge": 33.5,
            "m2.xlarge": 6.5,
            "m2.2xlarge": 13,
            "m2.4xlarge": 26,
            "cr1.8xlarge": 88,
            "i2.xlarge": 14,
            "i2.2xlarge": 27,
            "i2.4xlarge": 53,
            "i2.8xlarge": 104,
            "hs1.8xlarge": 35,
            "hi1.4xlarge": 35
        }

        self.actual_cpu_count = {
            "m3.medium": 1,
            "m3.large": 2,
            "m3.xlarge": 4,
            "m3.2xlarge": 8,
            "m1.small": 1,
            "m1.medium": 1,
            "m1.large": 2,
            "m1.xlarge": 4,
            "c3.large": 2,
            "c3.xlarge": 4,
            "c3.2xlarge": 8,
            "c3.4xlarge": 16,
            "c3.8xlarge": 32,
            "c1.medium": 2,
            "c1.xlarge": 8,
            "cc2.8xlarge": 32,
            "g2.2xlarge": 8,
            "cg1.4xlarge": 16,
            "m2.xlarge": 2,
            "m2.2xlarge": 4,
            "m2.4xlarge": 8,
            "cr1.8xlarge": 32,
            "i2.xlarge": 4,
            "i2.2xlarge": 8,
            "i2.4xlarge": 16,
            "i2.8xlarge": 32,
            "hs1.8xlarge": 16,
            "hi1.4xlarge": 16,
            "t1.micro": 1
        }

        self.normal_arch = [
            "c1.medium",
            "c1.xlarge",
            "c3.2xlarge",
            "c3.4xlarge",
            "c3.8xlarge",
            "c3.large",
            "c3.xlarge",
            "m1.large",
            "m1.medium",
            "m1.small",
            "m1.xlarge",
            "m2.2xlarge",
            "m2.4xlarge",
            "m2.xlarge",
            "m3.2xlarge",
            "m3.large",
            "m3.medium",
            "m3.xlarge"
        ]

    def GetCpuCount(self, arch):
        return self.actual_cpu_count.get(arch, 1)

    def GetPerECorePrice(self, arch, total_price):
        if arch in self.expected_cpu_count.keys():
            return total_price / self.expected_cpu_count[arch]
        return total_price

    def GetSpotPrice(self, arch, per_ecore_price):
        if arch in self.expected_cpu_count.keys():
            return self.expected_cpu_count[arch] * per_ecore_price
        return 0.0

class SpotConfig:
    def __init__(self):
        self.bid_price = 0.0
        self.core_bid_price = 0.0
        self.max_nodes = 0
        self.min_nodes = 0
        self.region = 'us-east-1'
        self.ami = 'ami-951524fc'
        self.instance_type = 'c1.medium'
        self.allowed_instance_types = SpotCPU().normal_arch

    def LoadFromJsonString(self, parsed):
        if 'bid_price' in parsed.keys():
            self.bid_price = float(parsed['bid_price'])
        if 'core_bid_price' in parsed.keys():
            self.core_bid_price = float(parsed['core_bid_price'])
        if 'min_nodes' in parsed.keys():
            self.min_nodes = int(parsed['min_nodes'])
        if 'max_nodes' in parsed.keys():
            self.max_nodes = int(parsed['max_nodes'])
        if 'instance_type' in parsed.keys():
            self.instance_type = parsed['instance_type']
            self.allowed_instance_types = [self.instance_type]
        self.region = parsed['region']
        if self.region is None or len(self.region) == 0:
            self.region = 'us-east-1'

    def IsOkArch(self, arch):
        return arch in self.allowed_instance_types

    def IsOkArchPrice(self, arch, price):
        if not self.IsOkArch(arch):
            return False
        if price > self.bid_price:
            return False
        if SpotCPU().GetPerECorePrice(arch, price) > self.core_bid_price:
            return False
        return True

    def LoadFromFile(self, filename):
        self.LoadFromJsonString(open(filename).read())

    def IsValid(self):
        return self.bid_price > 0.0 and self.max_nodes > 0 and len(self.region) > 0
        
