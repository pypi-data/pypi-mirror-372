# Gufo Liftbridge

*An asynchronous [Python][Python] [Liftbridge][Liftbridge] client*

[![PyPi version](https://img.shields.io/pypi/v/gufo_liftbridge.svg)](https://pypi.python.org/pypi/gufo_liftbridge/)
![Downloads](https://img.shields.io/pypi/dw/gufo_liftbridge)
![Python Versions](https://img.shields.io/pypi/pyversions/gufo_liftbridge)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
![Build](https://img.shields.io/github/actions/workflow/status/gufolabs/gufo_liftbridge/py-tests.yml?branch=master)
![Sponsors](https://img.shields.io/github/sponsors/gufolabs)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)
---

**Documentation**: [https://docs.gufolabs.com/gufo_liftbridge/](https://docs.gufolabs.com/gufo_liftbridge/)

**Source Code**: [https://github.com/gufolabs/gufo_liftbridge/](https://github.com/gufolabs/gufo_liftbridge/)

---

*Gufo Liftbridge* is the Python asyncio Liftbridge client library. It hides complex cluster
topology management handling tasks and the internals of the gRPC as well. Client offers
following features:

* Publishing.
* Subscribing.
* Bulk publishing.
* Cursors manipulation.
* Cluster metadata fetching.
* Stream creating and destroying.
* Transparent data compression (own extension, may be not compatible with other clients).

## Installing

```
pip install gufo_liftbridge
```

## Publishing

``` python
from gufo.liftbridge.client import LiftbridgeClient

async def publish():
    async with LiftbridgeClient(["127.0.0.1:9292"]) as client:
        await client.publish(b"mybinarydata", stream="test", partition=0)
```

## Subscribing

``` python
from gufo.liftbridge.client import LiftbridgeClient

async def subscribe():
    async with LiftbridgeClient(["127.0.0.1:9292"]) as client:
        async for msg in client.subscribe("test", partition=0):
            print(f"{msg.offset}: {msg.value}")
```

## Features

* Clean async API.
* High-performance.
* Built with security in mind.
* Full Python typing support.
* Editor completion.
* Well-tested, battle-proven code.

## On Gufo Stack

This product is a part of [Gufo Stack][Gufo Stack] - the collaborative effort 
led by [Gufo Labs][Gufo Labs]. Our goal is to create a robust and flexible 
set of tools to create network management software and automate 
routine administration tasks.

To do this, we extract the key technologies that have proven themselves 
in the [NOC][NOC] and bring them as separate packages. Then we work on API,
performance tuning, documentation, and testing. The [NOC][NOC] uses the final result
as the external dependencies.

[Gufo Stack][Gufo Stack] makes the [NOC][NOC] better, and this is our primary task. But other products
can benefit from [Gufo Stack][Gufo Stack] too. So we believe that our effort will make 
the other network management products better.

[Gufo Labs]: https://gufolabs.com/
[Gufo Stack]: https://docs.gufolabs.com/
[NOC]: https://getnoc.com/
[Python]: https://python.org/
[Liftbridge]: https://liftbridge.io/
