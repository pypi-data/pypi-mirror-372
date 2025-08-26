import hashlib
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

# Import serialization utility
try:
    from utils.serialization_utils import to_serializable
except ImportError:
    try:
        # Fallback for when utils is not available as a top-level module
        from rust_crate_pipeline.utils.serialization_utils import \
            to_serializable
    except ImportError:
        # Fallback if import fails
        def to_serializable(obj: Any) -> Any:
            if hasattr(obj, "to_dict"):
                return obj.to_dict()
            elif hasattr(obj, "__dict__"):
                return obj.__dict__
            else:
                return str(obj)


class TrustVerdict(Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    DEFER = "DEFER"
    FLAG = "FLAG"

    def __str__(self) -> str:
        return self.value

    def to_json(self) -> str:
        return self.value


@dataclass
class SacredChainTrace:
    input_data: str
    context_sources: List[str]
    reasoning_steps: List[str]
    suggestion: str
    verdict: TrustVerdict
    audit_info: Dict[str, Any]
    irl_score: float
    execution_id: str
    timestamp: str
    canon_version: str

    def to_dict(self) -> Dict[str, Any]:
        """Converts the dataclass to a dictionary, handling enum serialization."""
        data = asdict(self)
        data["verdict"] = self.verdict.value
        return data

    def to_audit_log(self) -> str:
        # Use custom serialization to handle non-JSON objects
        data_dict = to_serializable(asdict(self))
        data_dict["verdict"] = self.verdict.value

        audit_data = {
            "execution_id": self.execution_id,
            "timestamp": self.timestamp,
            "sacred_chain": data_dict,
            "rule_zero_compliant": True,
        }

        return json.dumps(to_serializable(audit_data), indent=2)

    def verify_integrity(self) -> bool:
        chain_data = (
            f"{self.input_data}{self.context_sources}"
            f"{self.reasoning_steps}{self.suggestion}"
        )
        expected_hash = hashlib.sha256(chain_data.encode()).hexdigest()[:16]
        return expected_hash in self.execution_id


class SacredChainBase(ABC):
    def __init__(self) -> None:
        self.execution_log: List[SacredChainTrace] = []
        self.canon_version = "1.3.0"

    def generate_execution_id(self, input_data: str) -> str:
        datetime.now(timezone.utc).isoformat()
        data_hash = hashlib.sha256(input_data.encode()).hexdigest()[:8]
        unique_id = uuid.uuid4().hex[:8]
        return f"exec-{data_hash}-{unique_id}-{int(datetime.now().timestamp())}"

    def create_sacred_chain_trace(
        self,
        input_data: str,
        context_sources: List[str],
        reasoning_steps: List[str],
        suggestion: str,
        verdict: TrustVerdict,
        audit_info: Dict[str, Any],
        irl_score: float,
    ) -> SacredChainTrace:
        execution_id = self.generate_execution_id(input_data)
        timestamp = datetime.now(timezone.utc).isoformat()

        trace = SacredChainTrace(
            input_data=input_data,
            context_sources=context_sources,
            reasoning_steps=reasoning_steps,
            suggestion=suggestion,
            verdict=verdict,
            audit_info=audit_info,
            irl_score=irl_score,
            execution_id=execution_id,
            timestamp=timestamp,
            canon_version=self.canon_version,
        )

        self.execution_log.append(trace)
        return trace

    @abstractmethod
    async def analyze_with_sacred_chain(self, input_data: str) -> SacredChainTrace:
        pass

    def get_audit_summary(self) -> Dict[str, Any]:
        if not self.execution_log:
            return {"total_executions": 0, "verdicts": {}, "average_irl_score": 0.0}

        verdict_counts = {}
        total_irl_score = 0.0

        for trace in self.execution_log:
            verdict = trace.verdict.value
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
            total_irl_score += trace.irl_score

        return {
            "total_executions": len(self.execution_log),
            "verdicts": verdict_counts,
            "average_irl_score": total_irl_score / len(self.execution_log),
            "canon_version": self.canon_version,
            "last_execution": (
                self.execution_log[-1].timestamp if self.execution_log else None
            ),
        }
