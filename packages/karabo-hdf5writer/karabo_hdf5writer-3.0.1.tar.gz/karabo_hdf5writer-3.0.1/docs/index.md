# Hdf5Writer: a simple DAQ...

... that is `extra-data` compliant.

## Outline

This `Hdf5Writer` device will swallow any data that Karabo can produce
(well, except tables that is), and store it into HDF5 files which are
`extra-data` compliant.

Important actions and configuration options are accessible through the
device's `overview` scene:

![The overview scene](images/scene_overview.png)

## Interface

The interface is intended to be compatile to the EuXFEL DAQ in terms of states and commands. Currently, no "Pause" funtionality is implemented.
