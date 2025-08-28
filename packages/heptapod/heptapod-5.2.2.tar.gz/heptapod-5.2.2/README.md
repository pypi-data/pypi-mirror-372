# Python components of the Heptapod server

[![build status](https://foss.heptapod.net/heptapod/py-heptapod/badges/branch/default/build.svg)](https://foss.heptapod.net/heptapod/py-heptapod/commits/branch/default)
[![tests coverage](https://foss.heptapod.net/heptapod/py-heptapod/badges/branch/default/coverage.svg)](https://foss.heptapod.net/heptapod/py-heptapod/commits/branch/default)

[Heptapod](https://heptapod.net) is the friendly fork of GitLab that brings
Mercurial compatibility in. It is a system with multiple components, involving
several programmation languages, notably Ruby, Go and Python.

The purpose of this package is to centralize all Heptapod Python code that is
not (yet) in any other, more generic Python project (Mercurial, its extensions,
general-purpose libraries…), and keep them in a high state of quality.

## Scope and versioning policy

This Python project is not meant for anything else than being a component of
the Heptapod **server**, nor is it the whole of Heptapod, only
the parts that happen to be written in Python.

The interdependency with other Heptapod components is very tight, to the point
that the requirements file of Heptapod releases usually completely pins this
project. Starting with version
1.0.0 (for Heptapod 0.17), we are planning to follow
[semver](https://semver.org) rules (with PEP 440 for development versions).

Python 3 is fully supported since version 0.13.0, tested with 3.7 and 3.8.

[Python 2 support is deprecated](https://foss.heptapod.net/heptapod/heptapod/-/issues/353) as of version 1.0.0. Only the
`testhelpers` subpackage is fully supported for both Python versions,
because it can be used for more general Mercurial related testing.
Python 2 support will be dropped entirely when we will have a new home for
`testhelpers`.

## Development guide

### Launching the tests

We have unit and integration tests with `pytest`, they'd be typically
run in a virtualenv:

```
python 3 -m venv venv
source venv/bin/activate
./run-all-tests
```

We have a 100% coverage policy, that is enforced by `run-all-tests` and
therefore by the continuous integration.

This full run takes about 20 seconds in our continuous integration, and
usually less than that on developer workstations.

### Workflow rules

We follow the Heptapod default workflow. Please make a topic, and submit a
Merge Request.

Merge Request Pipelines have to pass, and coverage to stay at 100% for the MR
to be technically acceptable – we can help achieving these results, it's not
mandatory for submitting MRs and gather some feedback.


## Contents

### WSGI serving of repositories

Provided by `heptapod.wsgi` (not fully independent yet)


### Mercurial Hooks

`heptapod.hooks.check_publish.check_publish`:
   permission rules about public changesets in pushes.
`heptapod.hooks.git_sync.mirror`:
   synchronisation to inner auxiliary Git repository for exposition to GitLab
`heptapod.hooks.dev_util`: useful hooks for debug and development

### Mercurial extension

The `heptapod` extension will provide specific commands and generally everything
that should be done with full access to Mercurial internals.