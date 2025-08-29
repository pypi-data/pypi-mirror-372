'''
# RemotiveTopology framework

RemotiveTopology framework is a python library that allows you to easily interact with RemotiveTopology.
Using the framework you can create Behavioral Models or write test cases probing communication channels.

## Installation

.. code-block:: bash
    pip install remotivelabs-topology

## Project Links

- [Documentation](https://docs.remotivelabs.com/)
- [Examples](https://github.com/remotivelabs/remotivelabs-topology-examples)
- [Issues](mailto:support@remotivelabs.com)

## Usage

The RemotiveTopology Framework enables simulation of automotive ECUs and networks using Python.
It provides tools for modeling ECU behavior, sending and receiving real network traffic via RemotiveBroker,
and configuring communication over protocols like CAN and SOME/IP. The following sections describe how to define behavioral models,
configure namespaces, use the Restbus, handle inputs, and implement ECUs with flexible logic.

### Behavioral Models

A behavioral model in the RemotiveTopology Framework is a component that mimics the behavior of an ECU.
Like a real ECU, it is typically triggered by network messages, performs logic, and then sends new network messages to other components.
Behavioral models in RemotiveTopology will run on top of the RemotiveBroker, making them use real network protocols in their communication.

As with all nodes in a RemotiveTopology, a behavioral model communicates using real network traffic over protocols such as CAN buses or
SOME/IP networks. For a full list of supported network types, refer to the [RemotiveBroker documentation](https://docs.remotivelabs.com/docs/remotive-broker/configuration).

For more documentation, see `BehavioralModel`.
Below is the simplest way to use a behavioral model, although this one does nothing, except connecting to a RemotiveBroker.

```python
.. include:: _docs/snippets/behavioral_model.py
```

### Namespace

Refer to the [RemotiveBroker documentation](https://docs.remotivelabs.com/docs/remotive-broker/configuration)
for full configuration documentation.

.. include:: namespaces/__init__.py
    :start-after: """
    :end-line: -2

```python
.. include:: _docs/snippets/can_namespace.py
```

### The Restbus - Sending Periodic Network Messages

The communication on CAN buses, in particular, is often sent periodically, several times a second.
The `Restbus` can be used to accomplish this. You initiate a namespace, for example a `CanNamespace` with a list of messages that you would
like to send. The cycle time and the default value is normally taken from the signal database, but can be changed later on.

The restbus is configured by passing in a list of filters that will be applied to the signal databases.
They will produce a list of frames that should be sent by the restbus. In the example below, we use a filter that will match all frames
that can be sent on the `DriverCan0-HLCU` namespace by the `HazardLightControlUnit`. There are several filters to choose from.
See more in the section about [filters](#filters) below.

```python
.. include:: _docs/snippets/restbus.py
```

We can modify the values using the restbus context at any time. In this example, we update the `HazardLightButton`
signal within the `HazardLightButton` frame to `1`.

The restbus also supports assigning an array of values to a signal. When configured with multiple values, the restbus will cycle through
them sequentially, sending one value per tick, and repeat the sequence until reconfigured with new values.

By default, the restbus uses cycle times from the signal database. However, you can explicitly configure timing parameters using either
`cycle_time` or `delay_multiplier`:

```python
.. include:: _docs/snippets/restbus_config.py
    :start-line: 2
```

These timing parameters serve different purposes:

- `cycle_time_millis`: Sets a fixed cycle time for all signals matched by the filters, including non-cyclic ones.
This allows you to send non-cyclic signals at a fixed rate.
- `delay_multiplier`: Scales the cycle times of the signals by the specified factor. Use this to slow down the restbus (saving CPU) or
speed up testing. Note that it is the cycle time that is scaled,
so a larger value (> 1) will result slow things down and a small value (< 1) will speed things up.

### Input handlers

When starting the `BehavioralModel`, you can add handlers for incoming messages and react to them. In the previous section,
the **Hazard Light Control Unit** sent frames indicating whether the hazard light button was pressed.

Below is an example of another ECU taking that frame as input and printing a message whenever it is received:

```python
.. include:: _docs/snippets/input_handlers.py
```

As you can see, it's possible to set up multiple handlers in the array, but in the example we only add one single handler.
Each subscription will use filters to specify which messages that are of interest. More under [filters](#filters) below.

#### Filters

In the `remotivelabs.topology.namespaces.filters` package you can find several
filters that let you select a subset of all signals associated with an ECU.

All filters have a boolean flag called `include` that specifies if the filter is used to include or exclude messages. It defaults to `True`.

In most cases, filters are passed in an array, meaning that you can fine tune the selection by using include and exclude filters.
The orderof the filters does not matter, but exclusion filters have higher priority than inclusion.
Here are two examples; both will match all frames, except "Frame1".

```python
.. include:: _docs/snippets/filters.py
    :start-line: 2
```

## Logging

This library uses Python's standard `logging` module. By default, the library does not configure any logging handlers,
allowing applications to fully control their logging setup.

To enable logs from this library in your application or tests, configure logging as follows:

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("remotivelabs.topology").setLevel(logging.DEBUG)
```

For more advanced configurations, refer to the [Python logging documentation](https://docs.python.org/3/library/logging.html).

'''
# Imports in this file affect import paths and documentation

import logging

from remotivelabs.topology import behavioral_model, cli, control, ecu_mock, namespaces, testing, time

# Disable library logging by default
_logger = logging.getLogger("remotivelabs.topology")
_logger.addHandler(logging.NullHandler())

__all__ = [
    "behavioral_model",
    "namespaces",
    "control",
    "ecu_mock",
    "testing",
    "time",
    "cli",
]
