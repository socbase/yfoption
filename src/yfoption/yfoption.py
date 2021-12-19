from __future__ import print_function

import datetime as _datetime
import requests as _requests
import pandas as _pd
from collections import namedtuple as _namedtuple

_BASE_URL_ = 'https://query2.finance.yahoo.com'
user_agent_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

class Option():

    def __init__(self, ticker, session=None):
        self.ticker = ticker.upper()
        self._base_url = _BASE_URL_
        self._expirations = {}
        self._strikes = {}

    def _download_options(self, date=None, straddle=False, formatted=False, proxy=None):
        if date is None:
            url = "{}/v7/finance/options/{}?formatted={}&straddle={}".format(
                self._base_url, self.ticker, formatted, straddle)
        else:
            url = "{}/v7/finance/options/{}?date={}&straddle={}&formatted={}".format(
                self._base_url, self.ticker, date, straddle, formatted)

        # setup proxy in requests format
        if proxy is not None:
            if isinstance(proxy, dict) and "https" in proxy:
                proxy = proxy["https"]
            proxy = {"https": proxy}

        r = _requests.get(
            url=url,
            proxies=proxy,
            headers=user_agent_headers
        ).json()

        if len(r.get('optionChain', {}).get('result', [])) > 0:
            for exp in r['optionChain']['result'][0]['expirationDates']:
                self._expirations[_datetime.datetime.utcfromtimestamp(
                    exp).strftime('%Y-%m-%d')] = exp

            for strike in r['optionChain']['result'][0]['strikes']:
                self._strikes[strike] = strike

            opt = r['optionChain']['result'][0].get('options', [])
            return opt[0] if len(opt) > 0 else []

    def _options2df(self, opt, tz=None):
        data = _pd.DataFrame(opt).reindex(columns=[
            'contractSymbol',
            'lastTradeDate',
            'strike',
            'lastPrice',
            'bid',
            'ask',
            'change',
            'percentChange',
            'volume',
            'openInterest',
            'impliedVolatility',
            'inTheMoney',
            'contractSize',
            'currency'])

        data['lastTradeDate'] = _pd.to_datetime(
            data['lastTradeDate'], unit='s')
        if tz is not None:
            data['lastTradeDate'] = data['lastTradeDate'].tz_localize(tz)
        return data

    def option_chain(self, date=None, straddle=False, formatted=False, proxy=None, tz=None):
        if date is None:
            options = self._download_options(straddle=straddle, formatted=formatted, proxy=proxy)
        else:
            if not self._expirations:
                self._download_options()
            if date not in self._expirations:
                raise ValueError(
                    "Expiration `%s` cannot be found. "
                    "Available expiration are: [%s]" % (
                        date, ', '.join(self._expirations)))
            date = self._expirations[date]
            options = self._download_options(date=date, straddle=straddle, formatted=formatted, proxy=proxy)

        return _namedtuple('Options', ['calls', 'puts'])(**{
            "calls": self._options2df(options['calls'], tz=tz),
            "puts": self._options2df(options['puts'], tz=tz)
        })

    def option_straddle(self, date=None, formatted=False, proxy=None, tz=None):
        if date is None:
            options = self._download_options(straddle=True, formatted=formatted, proxy=proxy)
        else:
            if not self._expirations:
                self._download_options()
            if date not in self._expirations:
                raise ValueError(
                    "Expiration `%s` cannot be found. "
                    "Available expiration are: [%s]" % (
                        date, ', '.join(self._expirations)))

            date = self._expirations[date]
            options = self._download_options(date=date, straddle=True, formatted=formatted, proxy=proxy)

        return options['straddles']

    @property
    def options(self):
        if not self._expirations:
            self._download_options()
        return tuple(self._expirations.keys())

    @property
    def strikes(self):
        if not self._strikes:
            self._download_options()
        return tuple(self._strikes.keys())
