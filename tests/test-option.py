from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import yfoption as yf

if __name__ == '__main__':
    opt = yf.Option("AAPL")

    print(opt.option_straddle('2021-12-23'))



