__doc__ = """
Namespace access module for RemotiveBroker.

Provides an interface to a namespace configured in a RemotiveBroker.
Supported types include:
    - `someip`: Enables sending requests and subscribing to events.
    - `generic`: Enables Restbus access, signal subscriptions, and more.
    - `can`: Same as generic

Namespaces can be used standalone or injected into a BehavioralModel for simulation or testing.
See individual module documentation for protocol-specific details.
"""
