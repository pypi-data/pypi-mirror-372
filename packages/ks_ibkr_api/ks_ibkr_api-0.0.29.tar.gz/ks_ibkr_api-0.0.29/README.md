# binance_api

异常排查

```
发生异常: TypeError
BinanceWebsocketClient.__init__() got an unexpected keyword argument 'timeout'
  File "D:\GD\binance\binance_api\trade.py", line 102, in init_handlers
    setattr(self, f'{socket_client_names[security_type]}_trade', globals()[socket_client_methods[security_type]](on_message=message_callback_factory(on_message_trade, security_type)))
  File "D:\GD\binance\binance_api\trade.py", line 29, in __init__
    self.init_handlers(api_key=api_key, api_secret=api_secret, security_types=security_types)
  File "D:\GD\binance\main.py", line 167, in <module>
    main_trade = MainTrade(API_KEY, API_SECRET)
TypeError: BinanceWebsocketClient.__init__() got an unexpected keyword argument 'timeout'
```

原因：future的BinanceWebsocketClient库和spot的BinanceWebsocketClient库不一样，spot的可以兼容future，需要先安装future再安装spot，如果顺序不一致，需要先卸载spot在安装spot
