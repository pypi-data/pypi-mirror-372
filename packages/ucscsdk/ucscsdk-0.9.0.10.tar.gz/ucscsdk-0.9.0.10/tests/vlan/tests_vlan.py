# Copyright 2015 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from nose.tools import *
from ..connection.info import *
from ucscsdk.mometa.fabric.FabricLanCloud import FabricLanCloud
from ucscsdk.mometa.fabric.FabricVlan import FabricVlan

handle = None
vlan_id = "100"
vlan_name = "test_vlan100"


def setup():
    global handle
    handle = custom_setup()


def teardown():
    custom_teardown(handle)


@with_setup(setup, teardown)
def test_001_create_modify_vlan_global():
    global vlan_id, vlan_name
    mo = FabricLanCloud(parent_mo_or_dn="domaingroup-root/fabric/lan", mode="end-host",
                        vlan_compression="disabled", mac_aging="mode-default")
    dn = handle.query_dn("domaingroup-root/fabric/lan")
    mo = FabricVlan(
        parent_mo_or_dn="domaingroup-root/fabric/lan", name=vlan_name)

    handle.remove_mo(mo)
    handle.commit()
    handle.add_mo(mo)
    handle.commit()

    obj = handle.query_dn("domaingroup-root/fabric/lan/net-" + vlan_name)
    obj.id = vlan_id
    handle.set_mo(obj)
    handle.commit()


@with_setup(setup, teardown)
def test_001_delete_vlan_global():
    global vlan_name
    obj = handle.query_dn("domaingroup-root/fabric/lan/net-" + vlan_name)
    handle.remove_mo(obj)
    handle.commit()
