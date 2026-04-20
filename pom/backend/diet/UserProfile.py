import json
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any


@dataclass
class UserProfile:
    age: int
    gender: str                      # "male" / "female"
    weight: float                    # kg
    height: float                    # cm
    goal: str                        # "lose weight" / "maintain" / "gain weight"
    activity_level: str              # "sedentary","light","moderate","active","very_active"
    diet: Optional[str] = None       # "vegetarian", "vegan", etc.
    intolerances: Optional[List[str]] = None  # List of intolerances
    time_frame: str = "day"          # "day" or "week"
    prefer_ingredients: Optional[List[str]] = None
    num_meals: int = 3               # 3, 4, 5
    macro_profile: Optional[str] = None  # Balanced, High-Protein, etc.

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json(cls, json_str: str) -> 'UserProfile':
        data = json.loads(json_str)
        return cls(**data)
