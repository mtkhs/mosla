# Mosla: Slack Bot program

* Written in Python3.
* Easy to create your plugin with Python.
* slackclient v2.2.1 .
* You need to get both API token `xoxp` for transmit actively and `xoxb` for RTM connection.
  * https://api.slack.com/apps

## How to start

1. Clone and setup.
```
    $ git clone https://github.com/tkhs/mosla
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

