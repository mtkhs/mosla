# Mosla: Slack Bot program

* Written in Python3.
* Easy to create your plugin with Python.
* slackclient v3.1.0
* You need to create a **Classic Slack App** and **add a legacy bot user** scope.
  * https://api.slack.com/apps?new_classic_app=1
* You need to get both API token `xoxp` for transmit actively and `xoxb` for RTM connection.

## How to start

1. Clone and setup.
```
    $ git clone https://github.com/mtkhs/mosla
    $ cd mosla
    $ pip install -r requirements.txt
```
2. Create and edit the setting file.
```
    $ cp setting.toml{.example,}
    $ vim setting.toml
```
3. Run mosla.
```
    $ python mosla.py
```

