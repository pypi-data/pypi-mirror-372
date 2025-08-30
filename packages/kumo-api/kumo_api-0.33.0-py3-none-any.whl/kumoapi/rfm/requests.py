from typing import Any, Dict, List, Optional

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from kumoapi.common import ValidationResponse
from kumoapi.graph import GraphDefinition
from kumoapi.model_plan import RunMode
from kumoapi.rfm import Context, PQueryDefinition


@dataclass
class RFMValidateQueryRequest:
    query: str
    graph_definition: GraphDefinition


@dataclass
class RFMValidateQueryResponse:
    query_definition: PQueryDefinition
    validation_response: ValidationResponse


@dataclass
class RFMPredictRequest:
    context: Context
    run_mode: RunMode

    def to_protobuf(self) -> Any:
        import kumoapi.rfm.protos.request_pb2 as _request_pb2

        request_pb2: Any = _request_pb2

        msg = request_pb2.PredictRequest()
        self.context.fill_protobuf_(msg.context)
        msg.run_mode = getattr(request_pb2.RunMode, self.run_mode.upper())

        return msg

    def serialize(self) -> bytes:
        import kumoapi.rfm.protos.request_pb2 as _request_pb2

        request_pb2: Any = _request_pb2

        msg = request_pb2.PredictRequest()
        self.context.fill_protobuf_(msg.context)
        msg.run_mode = getattr(request_pb2.RunMode, self.run_mode.upper())

        return self.to_protobuf().SerializeToString()

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        import kumoapi.rfm.protos.request_pb2 as _request_pb2

        request_pb2: Any = _request_pb2

        msg = request_pb2.PredictRequest()
        msg.ParseFromString(data)

        return cls(
            context=Context.from_protobuf(msg.context),
            run_mode=RunMode(request_pb2.RunMode.Name(msg.run_mode).lower()),
        )


@dataclass
class RFMExplanationResponse:
    summary: str


@dataclass
class RFMPredictResponse:
    prediction: dict[str, Any]
    explanation: Optional[RFMExplanationResponse] = None


@dataclass
class RFMEvaluateRequest:
    context: Context
    run_mode: RunMode
    metrics: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.metrics is not None and len(self.metrics) == 0:
            self.metrics = None

    def to_protobuf(self) -> Any:
        import kumoapi.rfm.protos.request_pb2 as _request_pb2

        request_pb2: Any = _request_pb2

        msg = request_pb2.EvaluateRequest()
        self.context.fill_protobuf_(msg.context)
        msg.run_mode = getattr(request_pb2.RunMode, self.run_mode.upper())
        if self.metrics is not None:
            msg.metrics.extend(self.metrics)

        return msg

    def serialize(self) -> bytes:
        return self.to_protobuf().SerializeToString()

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        import kumoapi.rfm.protos.request_pb2 as _request_pb2

        request_pb2: Any = _request_pb2

        msg = request_pb2.EvaluateRequest()
        msg.ParseFromString(data)

        return cls(
            context=Context.from_protobuf(msg.context),
            run_mode=RunMode(request_pb2.RunMode.Name(msg.run_mode).lower()),
            metrics=list(msg.metrics),
        )


@dataclass
class RFMEvaluateResponse:
    metrics: Dict[str, Optional[float]]
