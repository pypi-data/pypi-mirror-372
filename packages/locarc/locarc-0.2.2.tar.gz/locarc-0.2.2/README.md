# Loc(al event) arc.

[![PyPI - Version](https://img.shields.io/pypi/v/locarc)](https://pypi.org/project/locarc/)

`locarc` is a tiny tool that aims to emulate an event driven stack locally for
testing and integration. It was primarily designed to reproduce an
[EventArc](https://cloud.google.com/eventarc/docs) use case where messages
are transiting from a [PubSub](https://cloud.google.com/pubsub/docs) topic to
an external service.

## Getting started

You can either run `locarc` by installing it with any Python package manager:

```bash
$ pip install locarc
```

or using the associated [Docker]() image from [DockerHub]():

```bash
$ docker run --rm -v /path/to/arc.yml:/locarc/arc.yml opsiedev/locarc --arcfile=/locarc/arc.yml
```

## The Arc file

> TBD
