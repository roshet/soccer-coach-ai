from dataclasses import dataclass, field


@dataclass
class CheckpointScore:
    name: str
    score: int          # 0-100
    flag: str | None    # Human-readable issue description, or None if passing


@dataclass
class BiomechanicsResult:
    technique: str
    scores: dict[str, int]
    flags: list[str]
    overall_score: int
    checkpoints: list[CheckpointScore] = field(default_factory=list)
