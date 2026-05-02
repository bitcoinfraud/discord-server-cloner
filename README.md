# server cloner

a simple python script that downloads the structure of a discord server and recreates (or not) it somewhere else. this includes roles, channels, emojis, stickers, and basic server info like name and icon.

## features

* downloads server data (roles, channels, emojis, stickers)
* saves everything locally as json
* recreates structure in another server
* restores server name and icon

## requirements

* python 3.10+
* required modules:

  * requests
  * fade

install dependencies with:

```
pip install requests fade
```

## usage

run the script:

```
python server_cloner.py
```

you will be asked for:

* your token
* the id of the server you want to copy

after downloading, you can choose to upload everything into another server by providing its id.

## how it works

the script uses discord's api to:

1. fetch data from a source server
2. store it locally inside a `data/` folder
3. recreate the structure in a target server using post/patch requests

## limitations

* channel permissions are not fully restored
* category structure may not match perfectly
* rate limits are not fully handled, so large servers may fail
* original ids are not preserved
* requires high permissions in the target server

## warnings

* using user tokens is against discord terms of service
* misuse of this tool can lead to account bans
* do not use this on servers you don’t own or have permission to modify

## notes

this project was made for learning and experimentation purposes. it's not optimized for stability or large-scale usage.

## author

ritual1337
