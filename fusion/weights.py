import yaml
from pathlib import Path
from config.settings import settings

class WeightRegistry:
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self._weights: dict[str, float] = {}
        self.load_weights()

    def load_weights(self) -> None:
        """Loads or reloads weights from the YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Weight config file not found: {self.config_path}")
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if "weights" in data:
                self._weights = data["weights"]
            else:
                self._weights = data
                
        # Basic validation: ensure weights roughly sum to 1.0
        total = sum(self._weights.values())
        if not (0.99 <= total <= 1.01):
            import structlog
            logger = structlog.get_logger()
            logger.warning("Weights do not sum to 1.0", total=total)

    def get_weight(self, signal_type: str) -> float:
        """Get the weight for a specific signal type. Defaults to 0.0 if not found."""
        return self._weights.get(signal_type, 0.0)

    def get_all_weights(self) -> dict[str, float]:
        """Returns a copy of all current weights."""
        return self._weights.copy()

# Singleton instance matching the settings path
weight_registry = WeightRegistry(settings.weights_path)
