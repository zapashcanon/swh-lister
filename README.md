swh-lister
==========

This component from the Software Heritage stack aims to produce listings
of software origins and their urls hosted on various public developer platforms
or package managers. As these operations are quite similar, it provides a set of
Python modules abstracting common software origins listing behaviors.

It also provides several lister implementations, contained in the
following Python modules:

- `swh.lister.bitbucket`
- `swh.lister.cgit`
- `swh.lister.cran`
- `swh.lister.debian`
- `swh.lister.gitea`
- `swh.lister.github`
- `swh.lister.gitlab`
- `swh.lister.gnu`
- `swh.lister.launchpad`
- `swh.lister.npm`
- `swh.lister.packagist`
- `swh.lister.phabricator`
- `swh.lister.pypi`

Dependencies
------------

All required dependencies can be found in the `requirements*.txt` files located
at the root of the repository.

Local deployment
----------------

## lister configuration

Each lister implemented so far by Software Heritage (`bitbucket`, `cgit`, `cran`, `debian`,
`gitea`, `github`, `gitlab`, `gnu`, `launchpad`, `npm`, `packagist`, `phabricator`, `pypi`)
must be configured by following the instructions below (please note that you have to replace
`<lister_name>` by one of the lister name introduced above).

### Preparation steps

1. `mkdir ~/.config/swh/`
2. create configuration file `~/.config/swh/listers.yml`

### Configuration file sample

Minimalistic configuration shared by all listers to add in file `~/.config/swh/listers.yml`:

```lang=yml
scheduler:
  cls: 'remote'
  args:
    url: 'http://localhost:5008/'

credentials: {}
```

Note: This expects scheduler (5008) service to run locally

## Executing a lister

Once configured, a lister can be executed by using the `swh` CLI tool with the
following options and commands:

```
$ swh --log-level DEBUG lister -C ~/.config/swh/listers.yml run --lister <lister_name> [lister_parameters]
```

Examples:

```
$ swh --log-level DEBUG lister -C ~/.config/swh/listers.yml run --lister bitbucket

$ swh --log-level DEBUG lister -C ~/.config/swh/listers.yml run --lister cran

$ swh --log-level DEBUG lister -C ~/.config/swh/listers.yml run --lister gitea url=https://codeberg.org/api/v1/

$ swh --log-level DEBUG lister -C ~/.config/swh/listers.yml run --lister gitlab url=https://salsa.debian.org/api/v4/

$ swh --log-level DEBUG lister -C ~/.config/swh/listers.yml run --lister npm

$ swh --log-level DEBUG lister -C ~/.config/swh/listers.yml run --lister pypi
```

Licensing
---------

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

See top-level LICENSE file for the full text of the GNU General Public License
along with this program.
