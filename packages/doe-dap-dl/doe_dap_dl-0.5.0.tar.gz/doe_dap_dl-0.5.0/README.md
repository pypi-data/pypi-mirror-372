# doe-dap-dl

This repository contains useful packages for Jupyter Notebook users to interact with data from WDH, Livewire, and the SPP data platform. Users will be able to import these packages and call high-level functions that handle all of the api calls, graphing, and interpolations to stream-line the end user's ability to analyze data.

## Example 1

```python
from doe_dap_dl import DAP
wdh = DAP('wdh.energy.gov')

wdh.setup_basic_auth(username='username', password='password')

# Search for files
filter = {
    'Dataset': 'wfip2/lidar.z04.a0',
    'date_time': {
        'between': ['20151004000000', '20151004020000']
    },
    'file_type': 'nc'
}

file_names = wdh.search(filter)

# Download files
files = wdh.download_files(file_names)
```

## Example 2

```python
from doe_dap_dl import DAP
wdh = DAP('wdh.energy.gov')

wdh.setup_basic_auth()

# Download files using order IDs
wdh.download_orders(order_ids=["order_id"])
```

[Main docs](https://github.com/DAP-platform/dap-py/blob/master/docs/doe_dap_dl.md)
[Search query docs](https://github.com/DAP-platform/dap-py/blob/master/docs/download-README.md)
[Plotting docs](https://github.com/DAP-platform/dap-py/blob/master/docs/plotting.md)
