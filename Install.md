## Download ##

LangBots is available throught the subversion repository:

```
$ svn checkout http://langbots.googlecode.com/svn/trunk/ langbots
```

## Dependencies ##

You need:
  * [Python](http://python.org/).
  * [PyGame](http://www.pygame.org/).
  * [PyYAML](http://pyyaml.org/).

On Debian/Ubuntu:

```
$ apt-get install python-pygame python-yaml
```

On ArchLinux:

```
$ pacman -Sy python-pygame pyyaml-python
```

## How to execute ##

For now the framework is not installable, so you must run it from the sources directory. You must also add the **langbots** root directory to the _PYTHONPATH_ environment variable:

```
$ cd /path/to/langbots
$ export PYTHONPATH=$PYTHONPATH:.
```

And now you should be able to run the main script:

```
$ langbots/main.py
```