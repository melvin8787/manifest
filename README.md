MonkehMod
=========

Getting Started
---------------

To get started with MonkehMod, you'll need to get
familiar with [Git and Repo](http://source.android.com/source/developing.html).

To initialize your local repository using the monkeys trees, use a command like this:

```shell
repo init -u git://github.com/MonkehMod/manifest.git -b kitkat
```

Then to sync up:

```shell
repo sync
```

Building
--------
<!-- build system information -->
<!-- mokee? -->

Submitting Patches
------------------
<!-- remote adding system (like cmgerrit command from cyanogen) -->
```shell
cd <project>

repo start kitkat .
<make all your changes>
repo upload .
```

<!-- carbondev/liquidsmooth readme also nice -->
