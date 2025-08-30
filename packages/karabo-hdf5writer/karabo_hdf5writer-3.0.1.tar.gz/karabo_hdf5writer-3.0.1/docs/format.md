
# Data Format

All data is stored "as if it were fast-data", i.e. no cloning takes
place for slow data, as it would in the full EuXFEL DAQ. This simplifies
data bookkeeping substantially.

In order to be compliant with extra-data needs, a fake `:slow` channel
specifier is introduced for slow data, and top-level `data` nodes are
created for any data source. A `RUN` data section is not created!

A resulting file structure might thus look like:

```bash
├INDEX
│ ├FOO
│ │ └BAR
│ │   ├test-mdl-08c59409-61fe-4745-afd8-186a82d1bcd6:output
│ │   │ └data
│ │   │   ├count  [uint64: 9]
│ │   │   └first  [uint64: 9]
│ │   └test-mdl-08c59409-61fe-4745-afd8-186a82d1bcd6:slow
│ │     └data
│ │       ├count  [uint64: 9]
│ │       └first  [uint64: 9]
│ ├flag   [int32: 9]
│ ├origin [int32: 9]
│ ├timestamp      [uint64: 9]
│ └trainId        [uint64: 9]
├INSTRUMENT
│ └FOO
│   └BAR
│     ├test-mdl-08c59409-61fe-4745-afd8-186a82d1bcd6:output
│     │ └data
│     │   └node
│     │     └ndarray      [int32: 1 × 100 × 200]
│     └test-mdl-08c59409-61fe-4745-afd8-186a82d1bcd6:slow
│       └data
│         ├node
│         │ ├counter      [uint32: 9]
│         │ └counterReadOnly      [uint32: 9]
│         ├state  [256-byte ASCII string: 9]
│         └vectors
│           └stringProperty       [256-byte ASCII string: 9 × 10]
└METADATA
    ...
```
