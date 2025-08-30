
# Configuration

To configure the device, add data sources to the `dataSources` table. You
will frequently want to do this as part of an offline configuration. The
meaning of the columns is as follows:

- **Device Id**: a Karabo device id. It does not need to be online when
  the table is edited, however, it does need to be online when `Configure`
  is clicked.

- **Properties**: a list of properties that are to be recorded from this
  device. If you add a node, all properties under that node are stored;
  if you add an output channel, the channel with all it's properties 
  is stored. In contrast to the main EuXFEL DAQ no specific syntax is
  required for an output channel.

- **Fail on Error**: Set this to true if you would like to ensure that if
  a device, or any of the properties you've configured to for it are not
  present and `ERROR` state is raised.  If you set this to false
  the aforementioned issues are logged, but do not result in error or
  an aborting data acquisition. This is useful for auxiliary data that might
  not always be present and will be ignore without having to reconfigure
  the data source list.

If the same device id is specified in multiple rows, then properties are
accumulated for this device. If fail on error is specified at least once
for a device, even across multiple rows, it will take affect for all
properties and channels specified for this device.

## Advanced Settings

The configurator panel additionally exposes the following expert options:

- **Output Directory**: runs will be stored in this directory. It is created
   on start-up if it doesn't exist. If previous runs exist in this directory
   they will be taken into account for the next run number. Existing data
   is thus not overwritten.

- **Device Connection Timeout**: the timeout in seconds before a failure
   to connect to a data source is considered an error. Depending on the
   device's *fail on error* setting a timeout results in either an
   `ERROR` state or only a log message.

- **Halt on Slow Data Ingestion Error**: enabling this will result in an
   acquisition run being aborted if a slow data handler raises an exception.
   If this is not enabled the issue will only be logged.

- **Halt on Fast Data Ingestion Error**: enabling this will result in an
   acquisition run being aborted if an output channel disconnects.
   If this is not enabled the issue will only be logged.

- **Maximum Wait Time for Data (trains)**: this configures the acceptance
   window for data. Data arriving with a latency greater than this time
   will not be acquired. The time also determines the latency for closing
   a run.

- **Maximum Vector Size if Unspecified**: This setting is relevant for
   vector properties. In order to store these vectors of a fixed length are
   assumed in the HDF5 file, and data shorter than this length is padded with
   1s while longer data is truncated (which will be indicated). A property
   can recommend a `maxSize` by having the corresponding attribute set. If
   no `maxSize` is given, then this value is taken instead.