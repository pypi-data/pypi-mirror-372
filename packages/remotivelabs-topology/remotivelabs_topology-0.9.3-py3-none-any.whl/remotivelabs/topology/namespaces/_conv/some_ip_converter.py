from __future__ import annotations

from dataclasses import dataclass
from typing import Union, cast

from remotivelabs.broker import Frame, SignalInfo, WriteSignal
from remotivelabs.topology.namespaces.some_ip.event import SomeIPEvent
from remotivelabs.topology.namespaces.some_ip.request import RequestType, SomeIPRequest
from remotivelabs.topology.namespaces.some_ip.response import ReturnCode, SomeIPError, SomeIPResponse


@dataclass(frozen=True)
class _Meta:
    session_id: int
    client_id: int


def some_ip_request_to_signals(request: SomeIPRequest, client_id: int, session_id: int) -> list[WriteSignal]:
    """
    Convert a SomeIPRequest into a list of Signal objects.
    """
    base_name = f"{request.service_instance_name}.Request.{request.name}"
    signals: list[WriteSignal] = [
        WriteSignal(name=f"{base_name}.Meta.ClientID", value=client_id),
        WriteSignal(name=f"{base_name}.Meta.SessionID", value=session_id),
        WriteSignal(name=f"{base_name}.Meta.MessageType", value=request.message_type),
    ]

    if request.raw:
        signals.append(WriteSignal(name=base_name, value=request.raw))
    else:
        signals.extend([WriteSignal(name=f"{base_name}.{key}", value=value) for key, value in request.parameters.items()])

    return signals


def some_ip_response_to_signals(
    response: SomeIPResponse | SomeIPError,
    service_instance_name: str,
    method_name: str,
    meta: _Meta,
) -> list[WriteSignal]:
    """
    Convert a SomeIPResponse or SomeIPError into a list of Signal objects.
    """
    base_name = f"{service_instance_name}.Response.{method_name}"
    signals: list[WriteSignal] = [
        WriteSignal(name=f"{base_name}.Meta.ClientID", value=meta.client_id),
        WriteSignal(name=f"{base_name}.Meta.SessionID", value=meta.session_id),
    ]

    if isinstance(response, SomeIPResponse):
        signals.append(WriteSignal(name=f"{base_name}.Meta.ReturnCode", value=ReturnCode.E_OK))
        if response.raw:
            signals.append(WriteSignal(name=base_name, value=response.raw))
        else:
            signals.extend([WriteSignal(name=f"{base_name}.{key}", value=value) for key, value in response.parameters.items()])
    elif isinstance(response, SomeIPError):
        signals.append(WriteSignal(name=f"{base_name}.Meta.ReturnCode", value=response.return_code))

    return signals


def some_ip_event_to_signals(
    event: SomeIPEvent,
) -> list[WriteSignal]:
    signals: list[WriteSignal] = []
    base_name = f"{event.service_instance_name}.Event.{event.name}"

    if event.raw:
        signals.append(WriteSignal(name=base_name, value=event.raw))
    else:
        signals.extend([WriteSignal(name=f"{base_name}.{key}", value=value) for key, value in event.parameters.items()])

    if not signals:
        signals.append(WriteSignal(name=base_name, value=b""))

    return signals


def frame_to_some_ip_request(frame: Frame) -> tuple[SomeIPRequest, _Meta]:
    """
    Decode a frame to a SOME/IP request and metadata tuple
    """
    [service, name] = frame.name.split(".Request.", 2)
    signals = {param_name.replace(frame.name, "").strip("."): value for param_name, value in frame.signals.items()}

    # Make sure Meta signals are popped
    session_id = cast(int, signals.pop("Meta.SessionID"))
    client_id = cast(int, signals.pop("Meta.ClientID"))
    message_type = RequestType(cast(int, signals.pop("Meta.MessageType")))

    return (
        SomeIPRequest(
            name=name.strip("."), service_instance_name=service, parameters=signals, raw=cast(bytes, frame.value), message_type=message_type
        ),
        _Meta(session_id=session_id, client_id=client_id),
    )


def frame_to_some_ip_response(frame: Frame, signal_infos: dict[str, SignalInfo]) -> tuple[SomeIPResponse | SomeIPError, _Meta]:
    """
    Decode a grpc signals object into a response object.
    """
    signals = {param_name.replace(frame.name, "").strip("."): value for param_name, value in frame.signals.items()}

    # Extract Meta signals
    session_id = cast(int, signals.pop("Meta.SessionID"))
    client_id = cast(int, signals.pop("Meta.ClientID"))
    return_code = signals.pop("Meta.ReturnCode")

    rc = return_code
    if f"{frame.name}.Meta.ReturnCode" in signal_infos.keys():
        rc = signal_infos[f"{frame.name}.Meta.ReturnCode"].value_names.get(cast(str, return_code), return_code)

    if rc == ReturnCode.E_OK:
        return (
            SomeIPResponse(parameters=signals, raw=cast(bytes, frame.value)),
            _Meta(session_id=session_id, client_id=client_id),
        )

    return (
        SomeIPError(return_code=cast(Union[str, int], return_code)),
        _Meta(session_id=session_id, client_id=client_id),
    )


def frame_to_some_ip_event(frame: Frame) -> SomeIPEvent:
    """
    Decode a frame to a SOME/IP event
    """
    [service, name] = frame.name.split(".Event.", 2)
    signals = {param_name.replace(frame.name, "").strip("."): value for param_name, value in frame.signals.items()}

    return SomeIPEvent(
        raw=cast(bytes, frame.value),
        name=name.strip("."),
        service_instance_name=service,
        parameters=signals,
    )
