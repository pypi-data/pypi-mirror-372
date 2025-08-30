from datetime import datetime

import numpy as np
import pytest
import pytest_asyncio  # noqa
from extra_data import RunDirectory, validation

from karabo.middlelayer import (
    QuantityValue, State, TimeMixin, Timestamp, sleep)
from karabo.middlelayer.testing import event_loop_policy  # noqa
from karabo.middlelayer.testing import (
    AsyncDeviceContext, create_instanceId, sleepUntil)
from karabo.middlelayer_devices.property_test import PropertyTest

from ..hdf5writer import Hdf5Writer


# a fixture to create a temporary path for tests
@pytest.fixture(scope="session")
def tmp_run_dir(tmp_path_factory):
    tmp_path_factory.mktemp("runs")
    return tmp_path_factory.getbasetemp().as_posix()


@pytest.mark.timeout(120)
@pytest.mark.asyncio
async def test_acquisition(tmp_run_dir):
    ptest_id = f"FOO/BAR/{create_instanceId()}"
    maximumWaitForData = 30
    _PTEST_CONFIG_ = {
        "deviceId": f"{ptest_id}",
    }

    _HDFWRITER_CONFIG_ = {
        "deviceId": f"{create_instanceId()}",
        "dataSources": [
            {
                "deviceId": ptest_id,
                "properties": [
                    "state",
                    "node",
                    "output",
                    "vectors.stringProperty",
                ],
                "failOnError": False,
            }
        ],
        "maximumWaitForData": maximumWaitForData,
        "outputDir": tmp_run_dir,
        "trainsPerSequenceFile": 10,
    }

    pdevice = PropertyTest(_PTEST_CONFIG_)
    blackhole = Hdf5Writer(_HDFWRITER_CONFIG_)

    async with AsyncDeviceContext(pdevice=pdevice, blackhole=blackhole) as ctx:
        assert ctx.instances["pdevice"] is pdevice
        assert ctx.instances["blackhole"] is blackhole

        # we start with valid configurations
        await sleepUntil(lambda: blackhole.state == State.PASSIVE)
        await blackhole.configure()
        assert blackhole.state == State.IGNORING, blackhole.status
        expected_msg = "Data from 4 properties, and 1 channels distributed on 1 devices will be acquired!"  # noqa
        assert expected_msg in blackhole.status

        await pdevice.startWritingOutput()

        await blackhole.monitor()
        assert blackhole.state == State.MONITORING
        assert blackhole.slow_ingestion_task is not None
        assert blackhole.data_worker_task is not None
        ts5 = None
        for i in range(10):
            TimeMixin.set_reference(
                i, int(datetime.now().timestamp()), 0, 50000
            )
            pdevice.node.counterReadOnly = i
            if i == 5:
                ts5 = pdevice.node.counterReadOnly.timestamp
            await sleep(0.1)
        # update a value in the past
        pdevice.node.counterReadOnly = QuantityValue(100, timestamp=ts5)
        await sleep(0.5)
        assert (
            len(blackhole.data) >= 10
        )  # will contain 10 updates of slow data + the output channel
        assert ts5.tid in blackhole.data
        found_channel = False
        for tid, sources in sorted(blackhole.data.items(), key=lambda k: k[0]):
            if f"{ptest_id}:output" in sources:
                found_channel = True

            if f"{ptest_id}:slow" not in sources:
                continue

            assert "node/counter" in sources[f"{ptest_id}:slow"]
            assert "node/counterReadOnly" in sources[f"{ptest_id}:slow"]
            assert "state" in sources[f"{ptest_id}:slow"]

            if tid == ts5.tid:
                assert (
                    sources[f"{ptest_id}:slow"]["node/counterReadOnly"] == 100
                )

        assert found_channel, blackhole.status

        # check that purging works - data should not grow indefinetly
        for i in range(50, 200):
            TimeMixin.set_reference(
                i, int(datetime.now().timestamp()), 0, 50000
            )
            ts = Timestamp()
            ts.tid = i
            pdevice.node.counterReadOnly = QuantityValue(i, timestamp=ts)
            await sleep(0.1)
            assert (
                len(blackhole.data) <= maximumWaitForData + 20
            )
            # we add a bit of buffer, since there's a 1 second delay on the
            # purge loop

        await blackhole.record()
        assert blackhole.state == State.ACQUIRING
        for i in range(200, 300):
            TimeMixin.set_reference(
                i, int(datetime.now().timestamp()), 0, 50000
            )
            ts = Timestamp()
            ts.tid = i
            pdevice.node.counterReadOnly = QuantityValue(i, timestamp=ts)
            await sleep(0.1)

        await blackhole.monitor()
        for i in range(300, 350):
            TimeMixin.set_reference(
                i, int(datetime.now().timestamp()), 0, 50000
            )
            ts = Timestamp()
            ts.tid = i
            pdevice.node.counterReadOnly = QuantityValue(i, timestamp=ts)
        assert blackhole.state == State.MONITORING

        # check data with extra-data validate
        val_result = validation.main([f"{tmp_run_dir}/r0001"])
        assert val_result is None

        # check the file contents
        rd = RunDirectory(f"{tmp_run_dir}/r0001")
        assert f"{ptest_id}:slow" in rd.all_sources
        assert f"{ptest_id}:output" in rd.all_sources
        assert rd.train_ids[0] >= 200
        assert rd.train_ids[-1] <= 300
        for idx in range(len(rd.train_ids)):
            tid, data = rd.train_from_index(idx)
            assert data[f"{ptest_id}:slow"]["data.node.counterReadOnly"] == tid
            assert data[f"{ptest_id}:slow"]["data.node.counter"] == 0
            assert data[f"{ptest_id}:slow"]["data.state"] == b"STARTED"
            assert data[f"{ptest_id}:slow"][
                "data.vectors.stringProperty"
            ].tolist() == [b"A", b"B", b"C", b"", b"", b"", b"", b"", b"", b""]

        assert np.count_nonzero(rd[f"{ptest_id}:output"].data_counts()) > 0

        # take as second run
        await blackhole.record()
        assert blackhole.state == State.ACQUIRING
        for i in range(350, 450):
            TimeMixin.set_reference(
                i, int(datetime.now().timestamp()), 0, 50000
            )
            ts = Timestamp()
            ts.tid = i
            pdevice.node.counterReadOnly = QuantityValue(i, timestamp=ts)
            await sleep(0.1)

        await blackhole.monitor()
        for i in range(450, 500):
            TimeMixin.set_reference(
                i, int(datetime.now().timestamp()), 0, 50000
            )
            ts = Timestamp()
            ts.tid = i
            pdevice.node.counterReadOnly = QuantityValue(i, timestamp=ts)
        assert blackhole.state == State.MONITORING

        # check data with extra-data validate
        val_result = validation.main([f"{tmp_run_dir}/r0002"])
        assert val_result is None

        # check the file contents
        rd = RunDirectory(f"{tmp_run_dir}/r0002")
        assert f"{ptest_id}:slow" in rd.all_sources
        assert f"{ptest_id}:output" in rd.all_sources
        assert rd.train_ids[0] >= 350
        assert rd.train_ids[-1] <= 450
        for idx in range(len(rd.train_ids)):
            tid, data = rd.train_from_index(idx)
            assert data[f"{ptest_id}:slow"]["data.node.counterReadOnly"] == tid
            assert data[f"{ptest_id}:slow"]["data.node.counter"] == 0
            assert data[f"{ptest_id}:slow"]["data.state"] == b"STARTED"
            assert data[f"{ptest_id}:slow"][
                "data.vectors.stringProperty"
            ].tolist() == [b"A", b"B", b"C", b"", b"", b"", b"", b"", b"", b""]

        assert np.count_nonzero(rd[f"{ptest_id}:output"].data_counts()) > 0

        # now do a full cycle to ignoring and back again
        await blackhole.ignore()
        assert blackhole.state == State.IGNORING
        assert blackhole.slow_ingestion_task is None
        assert blackhole.data_worker_task is None

        await blackhole.monitor()
        assert blackhole.state == State.MONITORING
        assert blackhole.slow_ingestion_task is not None
        assert blackhole.data_worker_task is not None
        print(blackhole.status)

        for i in range(500, 520):
            TimeMixin.set_reference(
                i, int(datetime.now().timestamp()), 0, 50000
            )
            ts = Timestamp()
            ts.tid = i
            pdevice.node.counterReadOnly = QuantityValue(i, timestamp=ts)
            await sleep(0.1)

        await blackhole.record()
        assert blackhole.state == State.ACQUIRING
        for i in range(520, 600):
            TimeMixin.set_reference(
                i, int(datetime.now().timestamp()), 0, 50000
            )
            ts = Timestamp()
            ts.tid = i
            pdevice.node.counterReadOnly = QuantityValue(i, timestamp=ts)
            await sleep(0.1)

        await blackhole.monitor()
        for i in range(600, 650):
            TimeMixin.set_reference(
                i, int(datetime.now().timestamp()), 0, 50000
            )
            ts = Timestamp()
            ts.tid = i
            pdevice.node.counterReadOnly = QuantityValue(i, timestamp=ts)
        assert blackhole.state == State.MONITORING

        # check data with extra-data validate
        val_result = validation.main([f"{tmp_run_dir}/r0003"])
        assert val_result is None

        # check the file contents
        rd = RunDirectory(f"{tmp_run_dir}/r0003")
        assert f"{ptest_id}:slow" in rd.all_sources
        assert f"{ptest_id}:output" in rd.all_sources
        assert rd.train_ids[0] >= 520
        assert rd.train_ids[-1] <= 600
        for idx in range(len(rd.train_ids)):
            tid, data = rd.train_from_index(idx)
            assert data[f"{ptest_id}:slow"]["data.node.counterReadOnly"] == tid
            assert data[f"{ptest_id}:slow"]["data.node.counter"] == 0
            assert data[f"{ptest_id}:slow"]["data.state"] == b"STARTED"
            assert data[f"{ptest_id}:slow"][
                "data.vectors.stringProperty"
            ].tolist() == [b"A", b"B", b"C", b"", b"", b"", b"", b"", b"", b""]
        assert np.count_nonzero(rd[f"{ptest_id}:output"].data_counts()) > 0

        await pdevice.stopWritingOutput()


@pytest.mark.timeout(120)
@pytest.mark.asyncio
async def test_acquisition_failure(tmp_run_dir):
    ptest_id = f"FOO/BAR/{create_instanceId()}"
    maximumWaitForData = 30
    _PTEST_CONFIG_ = {
        "deviceId": f"{ptest_id}",
    }

    _BLACKHOLE_CONFIG_ = {
        "deviceId": f"{create_instanceId()}",
        "dataSources": [
            {
                "deviceId": ptest_id,
                "properties": [
                    "state",
                    "node",
                    "output",
                    "vectors.stringProperty",
                ],
                "failOnError": False,
            }
        ],
        "maximumWaitForData": maximumWaitForData,
        "outputDir": tmp_run_dir,
        "trainsPerSequenceFile": 10,
    }

    pdevice = PropertyTest(_PTEST_CONFIG_)
    blackhole = Hdf5Writer(_BLACKHOLE_CONFIG_)

    async with AsyncDeviceContext(pdevice=pdevice, blackhole=blackhole) as ctx:
        assert ctx.instances["pdevice"] is pdevice
        assert ctx.instances["blackhole"] is blackhole

        # we start with valid configurations
        await sleepUntil(lambda: blackhole.state == State.PASSIVE)
        await blackhole.configure()
        assert blackhole.state == State.IGNORING, blackhole.status
        expected_msg = "Data from 4 properties, and 1 channels distributed on 1 devices will be acquired!"  # noqa
        assert expected_msg in blackhole.status

        await pdevice.startWritingOutput()

        await blackhole.monitor()
        assert blackhole.state == State.MONITORING
        assert blackhole.slow_ingestion_task is not None
        assert blackhole.data_worker_task is not None
        for i in range(10):
            TimeMixin.set_reference(
                i, int(datetime.now().timestamp()), 0, 50000
            )
            ts = Timestamp()
            ts.tid = i
            pdevice.node.counterReadOnly = QuantityValue(i, timestamp=ts)
            await sleep(0.1)
        await sleep(0.5)

        await blackhole.record()
        assert blackhole.state == State.ACQUIRING
        for i in range(200, 300):
            TimeMixin.set_reference(
                i, int(datetime.now().timestamp()), 0, 50000
            )
            ts = Timestamp()
            ts.tid = i
            if i < 250:
                pdevice.node.counterReadOnly = QuantityValue(i, timestamp=ts)
            # trigger an error that will disconnect the device
            if i == 250:
                await pdevice.slotKillDevice()
            await sleep(0.1)

        assert blackhole.data_worker_task is None
        assert blackhole.slow_ingestion_task is None
        assert blackhole.state == State.ERROR

        # check data with extra-data validate
        val_result = validation.main([f"{tmp_run_dir}/r0004"])
        assert val_result is None

        # check the file contents
        rd = RunDirectory(f"{tmp_run_dir}/r0004")
        assert f"{ptest_id}:slow" in rd.all_sources
        assert f"{ptest_id}:output" in rd.all_sources
        assert rd.train_ids[0] >= 200
        assert rd.train_ids[-1] <= 250
        for idx in range(len(rd.train_ids)):
            tid, data = rd.train_from_index(idx)
            assert data[f"{ptest_id}:slow"]["data.node.counterReadOnly"] == tid
            assert data[f"{ptest_id}:slow"]["data.node.counter"] == 0
            assert data[f"{ptest_id}:slow"]["data.state"] == b"STARTED"
            assert data[f"{ptest_id}:slow"][
                "data.vectors.stringProperty"
            ].tolist() == [b"A", b"B", b"C", b"", b"", b"", b"", b"", b"", b""]

        assert np.count_nonzero(rd[f"{ptest_id}:output"].data_counts()) > 0
