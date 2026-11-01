from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreWeights:
    primary_language: int = 25
    seniority: int = 20
    framework: int = 15
    complementary_stack: int = 15
    database: int = 10
    cloud_devops: int = 5
    workplace: int = 10
    experience_penalty: int = 5


SCORE_WEIGHTS = ScoreWeights()
