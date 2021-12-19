# Information
This package to only fetch option data from yahoo finance
## Installation
```bash
pip install yfoption

```
## Get options as straddle
* Get options of ticker as straddle
```bash
import yfoption as yf

opt = yf.Option("AAPL")
opt.option_straddle('2021-12-23')
```
## Get options
* Get options of ticker
```bash
import yfoption as yf

opt = yf.Option("AAPL")
opt.options
```

## Get strikes
* Get strikes of ticker
```bash
import yfoption as yf

opt = yf.Option("AAPL")
opt.strikes
```
