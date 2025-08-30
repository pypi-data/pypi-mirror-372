import os
import re
from asyncio import CancelledError, Future, TimeoutError, gather, wait_for
from collections.abc import Iterable
from datetime import datetime
from functools import partial
from typing import Self

import h5py
import numpy as np

from karabo.middlelayer import (
    AccessLevel, AccessMode, Assignment, Bool, Configurable, Device, Hash,
    HashType, KaraboValue, OutputProxy, PipelineMetaData, Proxy, Slot, State,
    String, TableValue, Timestamp, UInt32, Unit, VectorHash, VectorString,
    background, connectDevice, dtype_from_number, get_array_data, get_property,
    get_timestamp, getDevice, getSchema, newest_timestamp, sleep, slot,
    waitUntilNew)
from karabo.middlelayer.proxy import SubProxyBase

from ._version import __version__ as deviceVersion
from .scene import get_scene


class SelectionRow(Configurable):
    """The row schema for defining data sources"""

    deviceId = String(
        displayedName="Device Id", assignment=Assignment.MANDATORY
    )

    properties = VectorString(
        displayedName="Recorded Properties",
        assignment=Assignment.OPTIONAL,
        defaultValue=[],
        description="List of properties to record. Can contain output "
        "channels. If left empty the device will not be recorded.",
    )

    failOnError = Bool(
        displayedName="Fail on Error",
        assignment=Assignment.OPTIONAL,
        defaultValue=True,
        description="If false, then an error connecting to this device is a"
        " warning only, not an error!",
    )


class Hdf5Writer(Device):

    __version__ = deviceVersion

    availableScenes = VectorString(
        displayedName="Available Scenes",
        displayType="Scenes",
        accessMode=AccessMode.READONLY,
        defaultValue=["overview"]
    )

    warningsExist = Bool(
        displayedName="Warnings Exist",
        accessMode=AccessMode.READONLY,
        defaultValue=False,
        description="Will be true if any warnings were registered when "
        "configuring data sources, or connecting to them on entering "
        "the MONITORING state.",
    )

    dataIsTruncated = Bool(
        displayedName="Data is Truncated",
        accessMode=AccessMode.READONLY,
        defaultValue=False,
        description="Will be true if data is truncated due to maximum "
        "vector size constraints",
    )

    connectionTimeout = UInt32(
        displayedName="Device Connection Timeout",
        defaultValue=5,
        unitSymbol=Unit.SECOND,
        minInc=1,
        maxInc=60,
        assignment=Assignment.OPTIONAL,
        accessMode=AccessMode.RECONFIGURABLE,
        description="Timeout for trying to connect to a data source.",
        requiredAccessLevel=AccessLevel.EXPERT
    )

    haltOnSlowIngestionError = Bool(
        displayedName="Halt on Slow Data Ingestion Error",
        defaultValue=True,
        assignment=Assignment.OPTIONAL,
        accessMode=AccessMode.RECONFIGURABLE,
        allowedStates=[State.IGNORING, State.PASSIVE],
        description="If set to true a single exception in slow data "
        "ingestion will stop a run and result in an ERROR state.",
    )

    haltOnFastIngestionError = Bool(
        displayedName="Halt on Fast Data Ingestion Error",
        defaultValue=True,
        assignment=Assignment.OPTIONAL,
        accessMode=AccessMode.RECONFIGURABLE,
        allowedStates=[State.IGNORING, State.PASSIVE],
        description="If set to true a single exception in fast data "
        "ingestion will stop a run and result in an ERROR state.",
    )

    maximumWaitForData = UInt32(
        displayedName="Maximum wait time for data (trains)",
        defaultValue=50,
        minInc=0,
        maxInc=1000,
        assignment=Assignment.OPTIONAL,
        accessMode=AccessMode.RECONFIGURABLE,
    )

    defaultMaxVectorSize = UInt32(
        displayedName="Maximum vector size if unspecified",
        defaultValue=1000,
        minInc=1,
        assignment=Assignment.OPTIONAL,
        accessMode=AccessMode.RECONFIGURABLE,
        description="The maximum vector size to be used for `VECTOR_XYZ` "
        "properties if no `maxSize` is specified. Data is truncated if "
        "it exceeds this size.",
        requiredAccessLevel=AccessLevel.EXPERT,
    )

    dataSources = VectorHash(
        rows=SelectionRow,
        displayedName="Data Sources",
        defaultValue=[],
        assignment=Assignment.OPTIONAL,
        accessMode=AccessMode.RECONFIGURABLE,
        allowedStates=[State.PASSIVE, State.IGNORING],
        description="The data sources to be recorded during a run.",
    )

    numDevices = UInt32(
        displayedName="# Devices",
        accessMode=AccessMode.READONLY,
        defaultValue=0,
    )

    numSlowProperties = UInt32(
        displayedName="# Slow Properties",
        accessMode=AccessMode.READONLY,
        defaultValue=0,
    )

    numOutputChannels = UInt32(
        displayedName="# Output Channels",
        accessMode=AccessMode.READONLY,
        defaultValue=0,
    )

    outputDir = String(
        displayedName="Output Directory",
        assignment=Assignment.OPTIONAL,
        defaultValue=f"{os.environ['KARABO']}/var/data/runs",
        accessMode=AccessMode.RECONFIGURABLE,
        allowedStates=[State.PASSIVE, State.IGNORING, State.MONITORING],
        description="The output directory runs are written to.",
    )

    currentRunNumber = UInt32(
        displayedName="Current Run #",
        accessMode=AccessMode.READONLY,
    )

    currentSequenceFileNumber = UInt32(
        displayedName="Current Sequence File #",
        accessMode=AccessMode.READONLY,
    )

    trainsPerSequenceFile = UInt32(
        displayedName="Trains per Sequence File",
        assignment=Assignment.OPTIONAL,
        minInc=10,
        maxInc=10000,
        defaultValue=500,
        accessMode=AccessMode.RECONFIGURABLE,
        allowedStates=[State.PASSIVE, State.IGNORING, State.MONITORING],
        description="The maximumg number of trains in a sequence file",
    )

    def __init__(self, configuration: Hash) -> Self:
        super().__init__(configuration)
        # task that runs slow data ingestion during monitoring
        self.slow_ingestion_task = None
        # main worker loop, writes out data and purges outdated data
        self.data_worker_task = None
        # train at which a run is to start
        self.start_train = None
        # train at which a run is to end
        self.end_train = None
        # list of proxied output channels we maintain for disconnecting
        # when we leave monitoring.
        self.channel_proxies = []
        # the current data file
        self.current_file = None

    async def onInitialization(self) -> None:
        outdir = self.outputDir.value
        if not os.path.exists(outdir):
            os.makedirs(outdir, exist_ok=True)
            self.status = f"Created output dir at {outdir}!"
        self.state = State.PASSIVE

    def onDestruction(self) -> None:
        if self.slow_ingestion_task:
            self.slow_ingestion_task.cancel()

        if self.data_worker_task:
            self.data_worker_task.cancel()

    @Slot(displayedName="Reset")
    async def reset(self) -> None:
        # cancel any running tasks first,
        # then go back int passive state
        if self.slow_ingestion_task:
            self.slow_ingestion_task.cancel()

        if self.data_worker_task:
            self.data_worker_task.cancel()
        self.state = State.PASSIVE

    @Slot(
        displayedName="Configure",
        allowedStates=[State.PASSIVE, State.IGNORING],
    )
    async def configure(self) -> None:
        """Configures the data sources, and checks they are present.

        Will result in `self.source` containing a dictionary specifying the
        sources.

        The keys are the device ids, and then the values are a dictionaries
        with two lists, `slow_properties` for broker sources, and `channels`
        for pipeline sources.

        If a device specified as a source is not present, and
        `failOnError := True` for that source, this action results in
        `State.ERROR`. Otherwise only a warning is issued.

        If a property specified is not present on the source device, and
        `failOnError := True` for that
        source, this action results in `State.ERROR`. Otherwise only a
        warning is issued.

        If a property specified cannot be recorded and `failOnError := True`
        for that source, this action results in `State.ERROR`. Otherwise only a
        warning is issued.
        Permissible properties are values, nodes and output channels.
        Table elements cannot be recorded, slots cannot be recorded.

        If a specified property is a node, the properties specified in this
        node, and any subnodes are added with the same limitations as above.

        If the evaluation results in an empty list of to-be-recorded properties
        a warning is issued and the previous device state is retained.

        If a datasource is specified more than once, it is merged into a
        single specification. If any specification set 'failOnError := True'
        and all specifications on the same device will fail on error (at
        latest upon connection).

        If not failure occurs the resulting state is `State.IGNORING`.
        """
        self.sources = {}
        error_logs = []
        warning_logs = []
        logs = []
        prop_cnt = 0
        channel_cnt = 0

        # we make this an inline async function so that we can run
        # multiple evaluations concurrently.
        async def eval_one_device(device_id, properties, fail_on_error):
            nonlocal prop_cnt, channel_cnt
            try:
                d = await wait_for(
                    getDevice(device_id), timeout=self.connectionTimeout.value
                )
                device_spec = self.sources.setdefault(
                    device_id,
                    dict(
                        slow_properties=set(),
                        channels=set(),
                        fail_on_error=fail_on_error,
                    ),
                )

                # handle the case where a device is specified more than once
                # a single fail_on_error := True will trump all others
                device_spec["fail_on_error"] |= fail_on_error

                # check if all properties specified exist and if the are slow
                # or pipeline data
                for prop in properties:
                    if (
                        prop in device_spec["slow_properties"]
                        or prop in device_spec["channels"]
                    ):
                        # a double specification, we can avoid
                        continue
                    try:
                        # we need a recursion possibility here for nodes
                        def handle_one_prop(prop):
                            nonlocal prop_cnt, channel_cnt
                            p = get_property(d, prop)
                            # check if it's a pipeline channel
                            if isinstance(p, OutputProxy):
                                device_spec["channels"].add(prop)
                                channel_cnt += 1
                            elif isinstance(p, TableValue):
                                msg = f"Property {prop} is a table, and we cannot store tables!"  # noqa
                                if fail_on_error:
                                    error_logs.append(msg)
                                else:
                                    warning_logs.append(msg)
                            elif isinstance(p, KaraboValue):
                                device_spec["slow_properties"].add(prop)
                                prop_cnt += 1
                            elif isinstance(p, SubProxyBase):
                                logs.append(f"Recursing into node {prop}...")
                                for sub_prop in dir(p):
                                    # recurse into the node
                                    handle_one_prop(f"{prop}.{sub_prop}")
                            else:
                                msg = f"Property {prop} is neither a property, nor an output channel, but {type(p)}!"   # noqa
                                if fail_on_error:
                                    error_logs.append(msg)
                                else:
                                    warning_logs.append(msg)

                        handle_one_prop(prop)

                    except AttributeError:
                        msg = f"Property {prop} does not exist on {device_id}!"
                        if fail_on_error:
                            error_logs.append(msg)
                        else:
                            warning_logs.append(msg)

            except TimeoutError:
                msg = f"Connection to {device_id} timed out, skipping this device!"   # noqa
                if fail_on_error:
                    error_logs.append(msg)
                else:
                    warning_logs.append(msg)

        # we do this async.
        tasks = []
        for row in self.dataSources.to_hashlist():
            device_id = row["deviceId"]
            properties = row["properties"]
            fail_on_error = row["failOnError"]
            if len(properties) == 0:
                error_logs.append(
                    f"Skipping {device_id} because no properties are defined!"
                )
                continue
            tasks.append(eval_one_device(device_id, properties, fail_on_error))

        await gather(*tasks)

        if error_logs:
            self.status = "Failed configuring datasource:\n\n" + "\n".join(
                error_logs
            )
            self.state = State.ERROR
            return

        if prop_cnt == 0 and channel_cnt == 0:
            # nothing to do, stay in passive state
            logs.append("No data that can be acquired is configured")
            if warning_logs:
                logs.append("\nThe following warnings are present:\n\n")
                logs += warning_logs

            self.status = "\n".join(logs)
            return

        device_cnt = len(self.sources)
        if logs:
            logs.append("")
        logs.append(
            f"Data from {prop_cnt} properties, and {channel_cnt} channels distributed on {device_cnt} devices will be acquired!"   # noqa
        )
        self.numDevices = device_cnt
        self.numSlowProperties = prop_cnt
        self.numOutputChannels = channel_cnt

        self.warningsExist = len(warning_logs) > 0
        if warning_logs:
            logs.append("\nThe following warnings are present:\n\n")
            logs += warning_logs

        self.status = "\n".join(logs)
        self.state = State.IGNORING

    def ingest(self, timestamp: Timestamp, source: str, data: Hash) -> None:
        """Ingest `data` from `source` at `timestamp`.

        If `timestamp` is in the past the function will update existing data
        which is newer appropriately.

        All data is handles as if it were fast data, i.e. no cloning
        will be done to backfill value.
        """

        if self.boundary_train is not None:
            # we've already written this out and won't
            # handle after the fact data
            if timestamp.tid <= self.boundary_train:
                self.status = (
                    f"{source} produced data that cannot be written anymore"
                )
                return

        tid_data = self.data.setdefault(timestamp.tid, {})
        source_data = tid_data.setdefault(source, {})
        did_truncate = False

        # this recursion function will ensure that we log data in a way
        # that can be directly written out:
        # 1) ensure we have numpy arrays with the correct shape everywhere
        # 2) truncate data (and log this) so we don't exceed predefined
        #    max-sizes (in the file)
        # 3) harmonize paths so they will resolve directly to the correct
        #    h5py dataset.
        def recurse_data(tdata, prefix):
            nonlocal did_truncate
            for path, value in tdata.items():
                path = path.replace(".", "/")

                # numpy arrays are not directly disinguishable
                # we idenifiy them via a helper function
                # and then create an actual array
                if isinstance(value, Hash):
                    try:
                        # this will either return the array, or result
                        # in a key error if `value` does not represent
                        # an array.
                        value = get_array_data(value)
                    except KeyError:
                        # a Hash that is not a numpy array needs to be recursed
                        # into.
                        recurse_data(value, f"{prefix}/{path}")
                        continue

                # we do not want a leading /
                dpath = f"{prefix}/{path}".removeprefix("/")
                spath = f"/{source}/data/{dpath}"

                # skip any data that we don't plan on writing out
                if spath not in self.schemas:
                    continue

                # resolve Karabo data types to .value
                if hasattr(value, "value"):
                    value = value.value

                # at this point we will alreay have resolved Hashs
                # representing arrays into np.ndarrays
                # For all other data we need to prepare it into a numpy form
                if not isinstance(value, np.ndarray):
                    req_dtype = self.schemas[spath].dtype
                    if isinstance(value, list):
                        # pad to vector size
                        value = np.array(value, dtype=req_dtype)
                        req_size = self.schemas[spath].shape[1]

                        if req_size > value.size:
                            # strings have empty padding
                            if value.dtype == "S256":
                                constant = ""
                            else:
                                # everything else pads with 1 as per the EuXFEL
                                # DAQ behaviour
                                constant = 1

                            # we only right-pd, hence the (0, ...)
                            value = np.pad(
                                value,
                                (0, req_size - value.size),
                                mode="constant",
                                constant_values=constant,
                            )
                        elif req_size < value.size:
                            # in this case we need to truncate
                            value = value[:req_size]
                            did_truncate = True
                    else:
                        value = np.array(
                            [
                                value,
                            ],
                            dtype=req_dtype,
                        )
                # and finally we add a leading dimension, which corresponds
                # to the train axis we append and grow in HDF5
                source_data[dpath] = np.expand_dims(value, axis=0)

        recurse_data(data, "")
        self.dataIsTruncated = did_truncate

    def flatten_schemas(self) -> None:
        """Flatten schemas into a HDF5-compatible path hierarchy

        Specifically, this replaces "." with "/" in the path
        hierarchy combination of device ids ("/" separator)
        and Hash paths ("." separator).
        """
        # now traverse the schema history
        paths = {}

        def recurse_schema(schema, prefix):
            for path, spec in schema.items():
                path = path.replace(".", "/")
                if isinstance(spec, dict):
                    recurse_schema(spec, f"{prefix}/{path}")
                else:
                    paths[f"{prefix}/{path}"] = spec

        recurse_schema(self.schemas, "")
        self.schemas = paths

    def initialize_sequence_file(self, f: h5py.File) -> None:
        """Initialize the seqeunce file `f`.

        This function will create the INDEX and METADATAsections and
        all data templates required in the INSTRUMENT sections.

        It does not create a RUNDATA section because we handle
        all data as fast data.

        The function can be called in the MONITORING and
        ACQUIRING states when `self.sources` and `self.schemas`
        have been appropriately initialized.
        """
        max_trains = int(self.trainsPerSequenceFile.value)

        # top-level sources
        sources = [f"{s}:slow" for s in self.sources.keys()]
        # add channels
        for device_id, spec in self.sources.items():
            for channel in spec["channels"]:
                sources.append(f"{device_id}:{channel}")

        f.create_group("/INDEX")
        self.expected_index_sources = []
        for source in sources:
            self.expected_index_sources.append(source)
            f.create_group(f"/INDEX/{source}/data")
            f.create_dataset(
                f"/INDEX/{source}/data/count",
                (0,),
                maxshape=(max_trains,),
                dtype=np.uint64,
            )
            f.create_dataset(
                f"/INDEX/{source}/data/first",
                (0,),
                maxshape=(max_trains,),
                dtype=np.uint64,
            )

        f.create_dataset(
            "/INDEX/trainId", (0,), maxshape=(max_trains,), dtype=np.uint64
        )
        f.create_dataset(
            "/INDEX/timestamp", (0,), maxshape=(max_trains,), dtype=np.uint64
        )
        f.create_dataset(
            "/INDEX/flag", (0,), maxshape=(max_trains,), dtype=np.int32
        )
        f.create_dataset(
            "/INDEX/origin", (0,), maxshape=(max_trains,), dtype=np.int32
        )
        f.create_group("/INSTRUMENT")

        for path, spec in self.schemas.items():
            # first dimension has variable length, so we add it as 1,...
            shape = list(spec.shape)
            # and a maxsize of it equivalent to the chunk size, ...
            maxshape = [max_trains] + list(spec.shape)[1:]
            f.create_dataset(
                f"/INSTRUMENT/{path}",
                shape,
                maxshape=maxshape,
                dtype=spec.dtype,
            )

        # create the necessary metadata
        f.create_group("/METADATA")
        now = datetime.now().isoformat()
        f.create_dataset("/METADATA/creationDate", (1,), data=[now])
        f.create_dataset("/METADATA/updateDate", (1,), data=[now])
        f.create_dataset("/METADATA/daqLibrary", (1,), data=["42.0.0"])
        f.create_dataset("/METADATA/dataFormatVersion", (1,), data=["1.3"])
        f.create_dataset(
            "/METADATA/karaboFramework", (1,),
            data=[self.karaboVersion.value]
        )
        f.create_dataset(
            "/METADATA/proposalNumber", (1,), dtype=np.uint32,
            data=[42]
        )
        f.create_dataset(
            "/METADATA/runNumber",
            (1,),
            dtype=np.uint32,
            data=[self.currentRunNumber.value],
        )
        f.create_dataset(
            "/METADATA/sequenceNumber",
            (1,),
            dtype=np.uint32,
            data=[self.currentSequenceFileNumber.value],
        )
        # data sources are next
        f.create_group("/METADATA/dataSources")
        f.create_dataset(
            "/METADATA/dataSources/deviceId", (len(sources),),
            data=sources
        )
        f.create_dataset(
            "/METADATA/dataSources/dataSourceId",
            (len(sources),),
            data=[f"INSTRUMENT/{s}" for s in sources],
        )
        f.create_dataset(
            "/METADATA/dataSources/root",
            (len(sources),),
            data=["INSTRUMENT" for _ in sources],
        )

    async def data_worker(self) -> None:
        """The main data worker function.

        Here we write out data to file in the ACQUIRING state, and purge
        outdate data in the other states.
        """
        while self.state in [State.MONITORING, State.ACQUIRING]:
            # make sure we cast away unsignedness
            max_wait = int(self.maximumWaitForData.value)

            # trains we have
            trains_in_data = np.array(sorted(self.data.keys())).astype(
                np.int64
            )

            # if we have a train_id we rid ourselfs of any data before that
            if self.state == State.ACQUIRING or self.end_train is not None:
                assert self.current_file

                if self.start_train is not None:
                    to_purge = trains_in_data[
                        np.less(trains_in_data, int(self.start_train))
                    ]
                    for train in to_purge:
                        self.data.pop(train, None)
                    self.start_train = None
                to_write = trains_in_data[
                    np.less(
                        trains_in_data, int(get_timestamp().tid) - max_wait
                    )
                ]

                if to_write.size == 0:
                    await sleep(1)
                    continue

                self.boundary_train = to_write[
                    -1
                ]  # the last train we've written

                for train_id in sorted(to_write):
                    # this catches the case our end-train did not occur
                    # specifically and below is the one where we actually
                    # have the end train.
                    if (
                        self.end_train is not None
                        and train_id > self.end_train
                    ):
                        self.current_file.close()
                        self.end_train = None
                        break

                    sources = self.data.get(train_id)

                    # we can skip if there's not a single source
                    if sources is None:
                        continue

                    any_at_max_trains = False

                    # register the train
                    tpath = "/INDEX/trainId"
                    tdset = self.current_file[tpath]
                    tdset.resize(tdset.shape[0] + 1, axis=0)
                    tdset[tdset.shape[0] - 1, ...] = train_id
                    any_at_max_trains |= (
                        tdset.shape[0] == self.trainsPerSequenceFile.value - 1
                    )

                    # and the timestamp
                    tpath = "/INDEX/timestamp"
                    tdset = self.current_file[tpath]
                    tdset.resize(tdset.shape[0] + 1, axis=0)
                    tdset[tdset.shape[0] - 1, ...] = int(
                        datetime.now().timestamp() * 1000
                    )
                    any_at_max_trains |= (
                        tdset.shape[0] == self.trainsPerSequenceFile.value - 1
                    )

                    # and flags + originq
                    for dset in ["flag", "origin"]:
                        tpath = f"/INDEX/{dset}"
                        tdset = self.current_file[tpath]
                        tdset.resize(tdset.shape[0] + 1, axis=0)
                        tdset[tdset.shape[0] - 1, ...] = 0
                        any_at_max_trains |= (
                            tdset.shape[0]
                            == self.trainsPerSequenceFile.value - 1
                        )

                    expected_sources = self.expected_index_sources.copy()

                    for source, data in sources.items():
                        for path, value in data.items():
                            # fill in as if it is all fast data
                            # this avoids any requiredment of
                            # backfilling/cloning values like we do for
                            # slow data
                            spath = f"/INSTRUMENT/{source}/data/{path}"
                            if spath not in self.current_file:
                                continue
                            dset = self.current_file[spath]
                            dset.resize(dset.shape[0] + 1, axis=0)
                            dset[dset.shape[0] - 1, ...] = value

                            # this needs to trigger one train ahead of the
                            # maximum as we would resize upon the next train to
                            # a shape exceeding the maximum
                            any_at_max_trains |= (
                                dset.shape[0]
                                == self.trainsPerSequenceFile.value - 1
                            )

                        # update the index sections
                        # for where we had data
                        ipath = f"/INDEX/{source}/data"
                        fdset = self.current_file[f"{ipath}/first"]
                        cdset = self.current_file[f"{ipath}/count"]
                        # the 'first' location is determined by the
                        # count of the last entry.
                        if fdset.shape[0] > 0 and cdset.shape[0] > 0:
                            first = fdset[-1] + cdset[-1]
                        else:
                            # or 0 if we've started a fresh file.
                            first = 0
                        fdset.resize(fdset.shape[0] + 1, axis=0)
                        fdset[fdset.shape[0] - 1, ...] = first
                        cdset.resize(cdset.shape[0] + 1, axis=0)
                        cdset[cdset.shape[0] - 1, ...] = 1

                        expected_sources.remove(source)

                    # now update the index section for all sources that were
                    # missing
                    for source in expected_sources:
                        ipath = f"/INDEX/{source}/data"
                        cdset = self.current_file[f"{ipath}/count"]
                        fdset = self.current_file[f"{ipath}/first"]

                        # the 'first' location is determined by the
                        # count of the last entry.
                        if fdset.shape[0] > 0 and cdset.shape[0] > 0:
                            first = fdset[-1] + cdset[-1]
                        else:
                            # or 0 if we've started a fresh file.
                            first = 0

                        cdset.resize(cdset.shape[0] + 1, axis=0)
                        cdset[cdset.shape[0] - 1, ...] = 0
                        fdset.resize(fdset.shape[0] + 1, axis=0)
                        fdset[fdset.shape[0] - 1, ...] = first

                    if any_at_max_trains:
                        self.currentSequenceFileNumber += 1
                        self.current_file.close()
                        self.current_file = h5py.File(
                            self.path_template.format(
                                seq=self.currentSequenceFileNumber.value
                            ),
                            "w",
                        )
                        self.initialize_sequence_file(self.current_file)

                    if (
                        self.end_train is not None
                        and train_id == self.end_train
                    ):
                        self.current_file.close()
                        self.end_train = None
                        break

                to_purge = to_write
            else:
                to_purge = trains_in_data[
                    np.less(
                        trains_in_data, int(get_timestamp().tid) - max_wait
                    )
                ]
            for train in to_purge:
                self.data.pop(train, None)

            # we wait here ot buffer some data
            await sleep(1)

    async def slow_data_handler(
        self, proxy: Proxy, properties: Iterable[str]
    ) -> None:
        """Continuously ingests data from `proxy` for `properties`.

        This function implements a while loop which runs in the `MONITORING`
        and `ACQUIRING` states and uses `waitUntilNew` on `properties` to call
        `self.ingest` whenever a property updates.

        It will backfill data with older timestamps into the internal data
        structures, and can thus handle a mixture of timestamps on
        `properties`.
        """
        if len(properties) == 0:
            # nothing to do, might be expected, just return
            return

        latest_timestamps = {}
        while self.state in [State.MONITORING, State.ACQUIRING]:
            # need to get the newest train id amongst all props
            # and convert data to a Hash
            props = {p: get_property(proxy, p) for p in properties}

            # first update timestamps in the past
            for key, value in props.items():
                latest_timestamp = latest_timestamps.get(key)
                if latest_timestamp and latest_timestamp > value.timestamp:
                    self.ingest(
                        value.timestamp, proxy.deviceId.value, Hash(key, value)
                    )
                latest_timestamps[key] = value.timestamp

            # to fill up to the newest timestamp
            timestamp = newest_timestamp(props.values())
            hsh = Hash()
            for key, value in props.items():
                hsh[key] = value.value
            self.ingest(timestamp, f"{proxy.deviceId.value}:slow", hsh)

            await waitUntilNew(*list(props.values()))

    async def fast_data_handler(
        self, data: Hash, meta: PipelineMetaData
    ) -> None:
        """The data handler registered to pipeline outputs.

        The function will call `self.ingest` with this data. The function
        assumes that all data is of the same timestamp, which is
        `meta.timestamp`.
        """
        source = meta.source
        # get the timestamp object from timestamp variable
        timestamp = meta.timestamp.timestamp
        # make sure trainId is corrected
        timestamp = get_timestamp(timestamp)
        self.ingest(timestamp, source, data)

    async def fast_data_close_handler(self, source: str, _) -> None:
        """Handler called when an output channel is closed.

        If `haltOnFastIngestionError` is set to true, this will
        result in any running acquistion being terminated, and the device
        transitioning into an ERROR state.
        """
        if self.haltOnFastIngestionError:
            if self.data_worker_task is not None:
                self.data_worker_task.cancel()
                self.data_worker_task = None
            if self.slow_ingestion_task is not None:
                self.slow_ingestion_task.cancel()
                self.slow_ingestion_task = None
            if self.current_file is not None:
                self.current_file.close()
            self.state = State.ERROR
            self.status = f"Fast data ingestion failed for {source}, because channel disconnected"  # noqa

    async def _do_slow_ingestion(self, tasks: Iterable[Future]) -> None:
        """Performs slow ingestion for a group of proxies represented by
        `tasks`.

        Each task is a `slow_data_handler` task.

        If `haltOnSlowIngestionError` is set to true, an Exception in any task
        will result in any running acquistion being terminated, and the device
        transitioning into an ERROR state.
        """
        try:
            main_task = await gather(
                *tasks, return_exceptions=not self.haltOnSlowIngestionError
            )
        except Exception as e:
            if isinstance(e, CancelledError):
                # don't warn on CancelledError
                return
            self.state = State.ERROR
            self.status = f"Failed in slow ingestion task with {e}"
            main_task.cancel()
            if self.data_worker_task is not None:
                self.data_worker_task.cancel()
            if self.current_file is not None:
                self.current_file.close()

            return
        # if we didn't halt on an exception we still output any that happend
        for r in main_task:
            if isinstance(r, Exception) and not isinstance(r, CancelledError):
                self.status = (
                    f"Failed (but continued) in slow ingestion task with {r}"
                )

    @Slot(
        displayedName="Monitor",
        allowedStates=[State.IGNORING, State.ACQUIRING],
    )
    async def monitor(self) -> None:
        """Transitions the device to the `MONITORING` state.

        In the process all data sources are connected, and the slow and fast
        data handlers as well as the data worker are started.
        """
        if len(self.sources) == 0:
            self.status = "Refusing to monitor zero sources!"
            return

        if self.state == State.ACQUIRING:
            self.end_train = get_timestamp().tid
            self.state = State.MONITORING
            return

        # connect sources and retain proxies for recording
        self.data = {}
        self.schemas = {}
        self.boundary_train = None
        error_logs = []
        warning_logs = []
        tasks = []
        self.channel_proxies = []
        for device_id, specs in self.sources.items():
            slow_properties = specs["slow_properties"]
            channels = specs["channels"]
            fail_on_error = specs["fail_on_error"]
            try:
                proxy = await wait_for(
                    connectDevice(device_id),
                    timeout=self.connectionTimeout.value,
                )
                schema = await getSchema(proxy)
                # for extra-data to pick up these "fake" fast sources, we
                # need a colon in the source paht
                source_schema = self.schemas.setdefault(
                    f"{device_id}:slow/data", {}
                )
                # check if all properties we want are still in the schema
                # and connect output channels. This will catch any schema
                # updates that happened after configuration.
                for prop in slow_properties:
                    try:
                        p = get_property(proxy, prop)
                        if isinstance(p.value, np.ndarray):
                            shape = p.value.shape
                            dtype = p.value.dtype
                        else:
                            v_type = schema.getValueType(prop)
                            if (
                                v_type is HashType.VectorString
                                or v_type is HashType.String
                            ):
                                dtype = "S256"
                            else:
                                dtype = dtype_from_number(v_type.value)
                            if isinstance(p.value, list):
                                # a vector for which we need to evaluate the
                                # max size
                                hsh = schema.hash
                                if hsh.hasAttribute(prop, "maxSize"):
                                    shape = (0, int(hsh.getAttribute(prop, "maxSize")),)  # noqa
                                else:
                                    shape = (0, int(self.defaultMaxVectorSize.value),)  # noqa
                            else:
                                shape = (0,)
                        source_schema[prop] = np.ndarray(shape, dtype=dtype)
                    except AttributeError:
                        msg = f"Property {prop} does not exist on {device_id}, likely this is due to a schema update!!"  # noqa
                        if fail_on_error:
                            error_logs.append(msg)
                        else:
                            warning_logs.append(msg)

                if slow_properties:
                    # we need a handler for the slow data
                    tasks.append(
                        self.slow_data_handler(proxy, slow_properties)
                    )

                for channel in channels:
                    source_schema = self.schemas.setdefault(
                        f"{device_id}:{channel}/data", {}
                    )
                    try:
                        ch = get_property(proxy, channel)
                        ch.setDataHandler(self.fast_data_handler)
                        ch.setCloseHandler(
                            partial(
                                self.fast_data_close_handler,
                                f"{device_id}:{channel}",
                            )
                        )
                        # for channels schema evaluation is a bit more tricky
                        # we don't have data (guaranteed) at this point
                        channel_hsh = schema.hash[f"{channel}.schema"]

                        def eval_types(hsh, prefix):
                            for path in hsh.getKeys():
                                p = hsh[path]
                                if not isinstance(p, Hash):
                                    v_type = schema.getValueType(
                                        f"{channel}.schema.{prefix}{path}"
                                    )
                                    if (
                                        v_type is HashType.VectorString
                                        or v_type is HashType.String
                                    ):
                                        dtype = "S256"
                                    else:
                                        dtype = dtype_from_number(v_type.value)
                                    if isinstance(p.value, list):
                                        # a vector for which we need to
                                        # evaluate the max size
                                        if hsh.hasAttribute(path, "maxSize"):
                                            shape = (0, int(hsh.getAttribute(path, "maxSize")),)  # noqa
                                        else:
                                            shape = (0, int(self.defaultMaxVectorSize.value),)  # noqa
                                    else:
                                        shape = (0,)
                                    a = np.ndarray(shape, dtype=dtype)
                                    source_schema[f"{prefix}{path}"] = a
                                else:
                                    # this is a node (or an ND array)
                                    if (
                                        hsh.hasAttribute(path, "classId")
                                        and hsh.getAttribute(path, "classId")
                                        == "NDArray"
                                    ):
                                        arr_spec = hsh.get(path)
                                        shape = arr_spec[
                                            "shape", "defaultValue"]
                                        dtype = arr_spec[
                                            "type", "defaultValue"]
                                        a = np.ndarray(
                                            [1] + list(shape), dtype)
                                        source_schema[f"{prefix}{path}"] = a
                                    else:
                                        # the . at the end is important
                                        new_prefix = f"{prefix}{path}."
                                        eval_types(hsh[path], new_prefix)

                        eval_types(channel_hsh, "")

                        ch.connect()

                        # keep track of the channel proxy so we can disconnect
                        # it later.
                        self.channel_proxies.append(ch)

                    except AttributeError as e:
                        msg = f"Channel {channel} does not exist on {device_id}, likely this is due to a schema update! {e}"  # noqa
                        if fail_on_error:
                            error_logs.append(msg)
                        else:
                            warning_logs.append(msg)

            except TimeoutError:
                msg = f"Failed to connect to {device_id}!"
                if fail_on_error:
                    error_logs.append(msg)
                else:
                    warning_logs.append(msg)

        if error_logs:
            self.status = "Failed to transition to monitor:\n\n" + "\n".join(
                error_logs
            )
            self.state = State.ERROR
            return

        # makes schemas more parseable for h5py
        self.flatten_schemas()

        self.start_train = None  # we haven't started yet
        self.data_worker_task = background(self.data_worker())
        self.slow_ingestion_task = background(self._do_slow_ingestion(tasks))
        self.warningsExist = len(warning_logs) > 0
        logs = ["Transitioned to monitoring!"]
        if warning_logs:
            logs.append("\nThe following warnings are present:\n\n")
            logs += warning_logs

        self.status = "\n".join(logs)
        self.state = State.MONITORING

    @Slot(displayedName="Record", allowedStates=[State.MONITORING])
    async def record(self) -> None:
        """Starts a run."""
        assert self.data_worker_task is not None
        assert self.slow_ingestion_task is not None

        # prepare the file
        last_run = 0
        runs = os.listdir(self.outputDir)
        for run in runs:
            if not re.match(r"r[0-9]{4,4}", run):
                continue
            last_run = max(last_run, int(run.replace("r", "")))

        next_run = last_run + 1
        os.makedirs(f"{self.outputDir}/r{next_run:04d}", exist_ok=True)
        self.currentRunNumber = next_run
        self.currentSequenceFileNumber = 0
        self.path_template = f"{self.outputDir}/r{next_run:04d}/RAW-R{next_run:04d}-BLACKHOLE-S{{seq:05d}}.h5"  # noqa
        self.current_file = h5py.File(self.path_template.format(seq=0), "w")
        self.initialize_sequence_file(self.current_file)

        # set our start train id
        self.start_train = get_timestamp().tid
        self.end_train = None
        # the rest will happen in the data worker task
        self.state = State.ACQUIRING

    async def _do_ignore(self) -> None:
        """Background task that transitions to ignoring.

        Will wait for `maxWaitForData` to ensure all data is stored.
        """
        # if there's still an end train to be reached we need to wait
        # longer
        while self.end_train is not None:
            await sleep(0.5)

        # set the state first as it will end our workers
        self.state = State.CHANGING
        # disconnect the channel handles
        for ch in self.channel_proxies:
            ch.disconnect()
        self.channel_proxies.clear()

        if self.data_worker_task is not None:
            self.data_worker_task.cancel()
        if self.slow_ingestion_task is not None:
            self.slow_ingestion_task.cancel()

        self.data = {}
        self.schemas = {}
        self.data_worker_task = None
        self.slow_ingestion_task = None

    @Slot(displayedName="Ignore", allowedStates=[State.MONITORING])
    async def ignore(self) -> None:
        """Transition to the IGNORE state in which the data source
        configuration can be changed.
        """
        try:
            await wait_for(
                self._do_ignore(),
                timeout=self.maximumWaitForData.value / 10 + 2
            )
        except TimeoutError:
            self.status = "Timed out waiting for monitoring and data taking tasks to completed. Continuing nevertheless"  # noqa
        self.state = State.IGNORING

    @slot
    def requestScene(self, params):
        name = params.get('name', default='overview')
        payload = Hash(
            'success', True, 'name', name, 'data', get_scene(self.deviceId))

        return Hash('type', 'deviceScene',
                    'origin', self.deviceId,
                    'payload', payload)
