import copy

import pytest
import pytest_asyncio  # noqa

from karabo.middlelayer import Hash, State
from karabo.middlelayer.testing import event_loop_policy  # noqa
from karabo.middlelayer.testing import (
    AsyncDeviceContext, create_instanceId, sleepUntil)
from karabo.middlelayer_devices.property_test import PropertyTest

from ..hdf5writer import Hdf5Writer


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_configuration_simple(mocker):
    ptest_id = create_instanceId()
    _PTEST_CONFIG_ = {
        "deviceId": f"{ptest_id}",
    }

    _HDF5WRITER_CONFIG_ = {
        "deviceId": f"{create_instanceId()}",
        "dataSources": [
            {
                "deviceId": ptest_id,
                "properties": ["int32PropertyReadOnly"],
                "failOnError": True,
            }
        ],
    }

    pdevice = PropertyTest(_PTEST_CONFIG_)
    blackhole = Hdf5Writer(_HDF5WRITER_CONFIG_)

    async with AsyncDeviceContext(pdevice=pdevice, blackhole=blackhole) as ctx:
        assert ctx.instances["pdevice"] is pdevice
        assert ctx.instances["blackhole"] is blackhole

        # we start with valid configurations
        await sleepUntil(lambda: blackhole.state == State.PASSIVE)
        await blackhole.configure()
        assert blackhole.state == State.IGNORING
        expected_msg = "Data from 1 properties, and 0 channels distributed on 1 devices will be acquired!"  # noqa
        assert expected_msg in blackhole.status

        # device exists, but one property doesn't. We allow to fail though
        dataSources = blackhole.dataSources.to_hashlist()
        dataSources[0]["failOnError"] = False
        dataSources[0]["properties"].append("ThisDoesNotExist")
        blackhole.dataSources = dataSources
        await blackhole.configure()
        assert blackhole.state == State.IGNORING
        expected_msg = "Data from 1 properties, and 0 channels distributed on 1 devices will be acquired!"  # noqa
        assert expected_msg in blackhole.status
        expected_warning = (
            f"Property ThisDoesNotExist does not exist on {ptest_id}!"
        )
        assert expected_warning in blackhole.status

        # now change the behaviour to fail
        dataSources = blackhole.dataSources.to_hashlist()
        dataSources[0]["failOnError"] = True
        blackhole.dataSources = dataSources
        await blackhole.configure()
        assert blackhole.state == State.ERROR
        expected_error = (
            f"Property ThisDoesNotExist does not exist on {ptest_id}!"
        )
        assert expected_error in blackhole.status

        # go back to skipping but add a device that does not exist
        await blackhole.reset()
        dataSources = blackhole.dataSources.to_hashlist()
        dataSources[0]["failOnError"] = False
        # the copy here is important, otherwise we modify both rows below
        dataSources.append(copy.deepcopy(dataSources[0]))
        dataSources[1]["deviceId"] = "a/device/thatdoesntexist"
        blackhole.dataSources = dataSources
        await blackhole.configure()
        assert blackhole.state == State.IGNORING
        expected_msg = "Data from 1 properties, and 0 channels distributed on 1 devices will be acquired!"  # noqa
        assert expected_msg in blackhole.status
        expected_warning = "Connection to a/device/thatdoesntexist timed out, skipping this device!"  # noqa
        assert expected_warning in blackhole.status

        # remove all accessible properties from both devices
        await blackhole.reset()  # go to passive
        dataSources = blackhole.dataSources.to_hashlist()
        dataSources[0]["properties"] = ["somethingThatDoesntExist"]
        dataSources[1]["properties"] = ["int32PropertyReadOnly"]
        blackhole.dataSources = dataSources
        await blackhole.configure()
        assert blackhole.state == State.PASSIVE  # should stay in passive
        expected_msg = "No data that can be acquired is configured"
        assert expected_msg in blackhole.status

        # test merging
        dataSources = blackhole.dataSources.to_hashlist()
        dataSources[0]["properties"] = ["int32PropertyReadOnly"]
        dataSources[1] = copy.copy(dataSources[0])
        dataSources[1]["properties"] = [
            "state",
            "output",
            "int32PropertyReadOnly",
        ]
        blackhole.dataSources = dataSources
        await blackhole.configure()
        assert blackhole.state == State.IGNORING
        expected_msg = "Data from 2 properties, and 1 channels distributed on 1 devices will be acquired!"  # noqa
        assert expected_msg in blackhole.status


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_configuration_full(mocker):
    ptest_id = create_instanceId()
    _PTEST_CONFIG_ = {
        "deviceId": f"{ptest_id}",
    }

    pdevice = PropertyTest(_PTEST_CONFIG_)
    blackhole = Hdf5Writer({"deviceId": f"{create_instanceId()}"})

    async with AsyncDeviceContext(pdevice=pdevice, blackhole=blackhole) as ctx:
        assert ctx.instances["pdevice"] is pdevice
        assert ctx.instances["blackhole"] is blackhole

        # we define all properties the PropertyTest has
        properties = list(dir(pdevice))
        dataSources = [
            Hash(
                "deviceId",
                ptest_id,
                "properties",
                properties,
                "failOnError",
                False,
            )
        ]
        await sleepUntil(lambda: blackhole.state == State.PASSIVE)
        blackhole.dataSources = dataSources
        await blackhole.configure()
        assert blackhole.state == State.IGNORING
        table_warning = (
            "Property table is a table, and we cannot store tables!"
        )
        assert table_warning in blackhole.status
        node_msg = "Recursing into node log..."
        assert node_msg in blackhole.status
        node_msg = "Recursing into node node..."
        assert node_msg in blackhole.status
        node_msg = "Recursing into node vectors..."
        assert node_msg in blackhole.status
        # a bit fuzzy between Framework versions
        assert blackhole.numSlowProperties >= 61
        assert blackhole.numDevices == 1
        assert blackhole.numOutputChannels == 1
