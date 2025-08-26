"""
Machine Learning Quality Predictor for Rust Crates

Uses ML models to predict:
- Code quality scores
- Security risk levels
- Maintenance activity
- Popularity trends
- Dependency health
"""

import json
import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


@dataclass
class QualityPrediction:
    """Prediction results for crate quality."""

    crate_name: str
    quality_score: float
    security_risk: str
    maintenance_score: float
    popularity_trend: str
    dependency_health: float
    confidence: float
    features_used: List[str]
    model_version: str


class CrateQualityPredictor:
    """ML-based quality predictor for Rust crates."""

    def __init__(self, model_dir: str = "./models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Models
        self.quality_model: Optional[RandomForestRegressor] = None
        self.security_model: Optional[RandomForestClassifier] = None
        self.maintenance_model: Optional[RandomForestRegressor] = None
        self.popularity_model: Optional[RandomForestClassifier] = None
        self.dependency_model: Optional[RandomForestRegressor] = None

        # Feature processing
        self.text_vectorizer: Optional[TfidfVectorizer] = None
        self.scaler: Optional[StandardScaler] = None

        # Model metadata
        self.model_version = "1.0.0"
        self.feature_names: List[str] = []

        self._load_models()

    def _load_models(self) -> None:
        """Load trained models from disk."""
        try:
            model_files = {
                "quality": "quality_model.pkl",
                "security": "security_model.pkl",
                "maintenance": "maintenance_model.pkl",
                "popularity": "popularity_model.pkl",
                "dependency": "dependency_model.pkl",
                "vectorizer": "text_vectorizer.pkl",
                "scaler": "feature_scaler.pkl",
                "metadata": "model_metadata.json",
            }

            # Load metadata
            metadata_file = self.model_dir / model_files["metadata"]
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    self.model_version = metadata.get("version", "1.0.0")
                    self.feature_names = metadata.get("feature_names", [])

            # Load models
            for model_name, filename in model_files.items():
                if model_name in ["metadata"]:
                    continue

                model_file = self.model_dir / filename
                if model_file.exists():
                    with open(model_file, "rb") as f:
                        model = pickle.load(f)

                    if model_name == "quality":
                        self.quality_model = model
                    elif model_name == "security":
                        self.security_model = model
                    elif model_name == "maintenance":
                        self.maintenance_model = model
                    elif model_name == "popularity":
                        self.popularity_model = model
                    elif model_name == "dependency":
                        self.dependency_model = model
                    elif model_name == "vectorizer":
                        self.text_vectorizer = model
                    elif model_name == "scaler":
                        self.scaler = model

            self.logger.info("Loaded models")

        except Exception as e:
            self.logger.warning(f"Failed to load models: {e}")

    def _extract_features(self, crate_data: Dict[str, Any]) -> List[float]:
        """Extract numerical features from crate data."""
        try:
            features = []

            # Basic features (8 features)
            description = crate_data.get("description", "")
            features.append(len(description))
            features.append(len(description.split()) if description else 0)

            # Context and reasoning features
            context_sources = crate_data.get("context_sources", [])
            features.append(len(context_sources))

            reasoning_steps = crate_data.get("reasoning_steps", [])
            features.append(len(reasoning_steps))

            # IRL score
            features.append(float(crate_data.get("irl_score", 0.0)))

            # Audit info features
            audit_info = crate_data.get("audit_info", {})

            # Crate analysis features
            crate_analysis = audit_info.get("crate_analysis", {})
            enhanced_analysis = crate_analysis.get("enhanced_analysis", {})

            # Environment features
            environment = enhanced_analysis.get("environment", {})
            features.append(1.0 if environment.get("has_cargo_toml") else 0.0)
            features.append(1.0 if environment.get("has_dependencies") else 0.0)

            # Ensure we have exactly 8 basic features
            while len(features) < 8:
                features.append(0.0)
            features = features[:8]

            # Text features (100 features from TF-IDF)
            text_features = []
            if self.text_vectorizer is not None:
                try:
                    # Combine relevant text fields
                    text_content = " ".join(
                        [
                            description,
                            str(crate_data.get("readme_content", "")),
                            " ".join(context_sources),
                            " ".join([str(step) for step in reasoning_steps]),
                        ]
                    )

                    if text_content.strip():
                        text_vector = self.text_vectorizer.transform([text_content])
                        text_features = text_vector.toarray()[0].tolist()
                    else:
                        text_features = [0.0] * 100
                except Exception as e:
                    self.logger.warning(f"Text vectorization failed: {e}")
                    text_features = [0.0] * 100
            else:
                text_features = [0.0] * 100

            # Ensure exactly 100 text features
            while len(text_features) < 100:
                text_features.append(0.0)
            text_features = text_features[:100]

            # Analysis features (6 features)
            analysis_features = []

            # Environment features
            environment = enhanced_analysis.get("environment", {})
            analysis_features.append(
                1.0 if environment.get("has_dev_dependencies") else 0.0
            )
            analysis_features.append(len(environment.get("features", [])))

            # Source statistics
            source_stats = enhanced_analysis.get("source_stats", {})
            analysis_features.append(float(source_stats.get("rust_files", 0)))
            analysis_features.append(float(source_stats.get("rust_lines", 0)))
            analysis_features.append(1.0 if source_stats.get("has_tests") else 0.0)
            analysis_features.append(1.0 if source_stats.get("has_examples") else 0.0)

            # Ensure exactly 6 analysis features
            while len(analysis_features) < 6:
                analysis_features.append(0.0)
            analysis_features = analysis_features[:6]

            # Combine all features: 8 basic + 100 text + 6 analysis = 114 total
            all_features = features + text_features + analysis_features

            # Final validation
            if len(all_features) != 114:
                self.logger.warning(
                    f"Feature count mismatch: got {len(all_features)}, expected 114"
                )
                # Pad or truncate to exactly 114
                while len(all_features) < 114:
                    all_features.append(0.0)
                all_features = all_features[:114]

            return all_features

        except Exception as e:
            self.logger.warning(f"Feature extraction failed: {e}")
            # Return default feature vector with exactly 114 features
            return [0.0] * 114

    def _initialize_text_vectorizer(self, sample_texts: List[str]) -> None:
        """Initialize text vectorizer with sample data."""
        try:
            self.text_vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words="english",
                lowercase=True,
                ngram_range=(1, 2),
            )
            # Fit on sample texts
            if sample_texts and any(text.strip() for text in sample_texts):
                self.text_vectorizer.fit(sample_texts)
            else:
                # Fit on dummy data if no real text available
                self.text_vectorizer.fit(["sample text", "rust crate", "library"])
            self.logger.info("Initialized text vectorizer")
        except Exception as e:
            self.logger.error(f"Failed to initialize text vectorizer: {e}")
            self.text_vectorizer = None

    def _initialize_scaler(self) -> None:
        """Initialize feature scaler with default parameters."""
        try:
            self.scaler = StandardScaler()
            # We can't fit the scaler without training data
            # It will be fitted during training
            self.logger.info(
                "Initialized feature scaler (requires training data to fit)"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize scaler: {e}")
            self.scaler = None

    def _initialize_default_models(self) -> None:
        """Initialize models with default parameters for basic predictions."""
        try:
            # Create simple models that can provide basic predictions
            self.quality_model = RandomForestRegressor(n_estimators=10, random_state=42)
            self.security_model = RandomForestClassifier(
                n_estimators=10, random_state=42
            )
            self.maintenance_model = RandomForestRegressor(
                n_estimators=10, random_state=42
            )
            self.popularity_model = RandomForestClassifier(
                n_estimators=10, random_state=42
            )
            self.dependency_model = RandomForestRegressor(
                n_estimators=10, random_state=42
            )

            # Train on minimal dummy data to make models functional
            dummy_features = np.array([[0.5] * 114]).reshape(
                1, -1
            )  # 8 basic + 100 text + 6 analysis

            self.quality_model.fit(dummy_features, [0.5])
            self.security_model.fit(dummy_features, [1])  # medium risk
            self.maintenance_model.fit(dummy_features, [0.5])
            self.popularity_model.fit(dummy_features, [1])  # stable
            self.dependency_model.fit(dummy_features, [0.5])

            self.logger.info("Initialized default models with basic functionality")

        except Exception as e:
            self.logger.error(f"Failed to initialize default models: {e}")

    def ensure_models_available(self) -> None:
        """Ensure models are available for predictions."""
        models_missing = [
            self.quality_model is None,
            self.security_model is None,
            self.maintenance_model is None,
            self.popularity_model is None,
            self.dependency_model is None,
        ]

        if any(models_missing):
            self.logger.warning(
                "Some ML models are missing, initializing default models"
            )
            self._initialize_default_models()

    def predict_quality(self, crate_data: Dict[str, Any]) -> QualityPrediction:
        """Predict quality metrics for a crate."""
        try:
            # Ensure models are available before prediction
            self.ensure_models_available()

            features = self._extract_features(crate_data)

            # Make predictions
            quality_score = 0.5
            if self.quality_model:
                quality_score = float(self.quality_model.predict([features])[0])
                quality_score = max(0.0, min(1.0, quality_score))

            security_risk = "medium"
            if self.security_model:
                risk_pred = self.security_model.predict([features])[0]
                security_risk = ["low", "medium", "high"][risk_pred]

            maintenance_score = 0.5
            if self.maintenance_model:
                maintenance_score = float(self.maintenance_model.predict([features])[0])
                maintenance_score = max(0.0, min(1.0, maintenance_score))

            popularity_trend = "stable"
            if self.popularity_model:
                trend_pred = self.popularity_model.predict([features])[0]
                popularity_trend = ["declining", "stable", "growing"][trend_pred]

            dependency_health = 0.5
            if self.dependency_model:
                dependency_health = float(self.dependency_model.predict([features])[0])
                dependency_health = max(0.0, min(1.0, dependency_health))

            # Calculate confidence based on model availability
            models_available = sum(
                [
                    self.quality_model is not None,
                    self.security_model is not None,
                    self.maintenance_model is not None,
                    self.popularity_model is not None,
                    self.dependency_model is not None,
                ]
            )
            confidence = min(1.0, models_available / 5.0)

            return QualityPrediction(
                crate_name=crate_data.get("name", "unknown"),
                quality_score=quality_score,
                security_risk=security_risk,
                maintenance_score=maintenance_score,
                popularity_trend=popularity_trend,
                dependency_health=dependency_health,
                confidence=confidence,
                features_used=self.feature_names,
                model_version=self.model_version,
            )

        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return QualityPrediction(
                crate_name=crate_data.get("name", "unknown"),
                quality_score=0.5,
                security_risk="unknown",
                maintenance_score=0.5,
                popularity_trend="unknown",
                dependency_health=0.5,
                confidence=0.0,
                features_used=[],
                model_version=self.model_version,
            )

    def train_models(self, training_data: List[Dict[str, Any]]) -> None:
        """Train models on historical crate data."""
        if not training_data:
            self.logger.warning("No training data provided")
            return

        try:
            # Prepare training data
            X = []
            y_quality = []
            y_security = []
            y_maintenance = []
            y_popularity = []
            y_dependency = []

            for crate in training_data:
                features = self._extract_features(crate)
                X.append(features)

                # Extract labels
                y_quality.append(crate.get("quality_score", 0.5))
                y_security.append(
                    crate.get("security_risk_level", 1)
                )  # 0=low, 1=medium, 2=high
                y_maintenance.append(crate.get("maintenance_score", 0.5))
                y_popularity.append(
                    crate.get("popularity_trend", 1)
                )  # 0=declining, 1=stable, 2=growing
                y_dependency.append(crate.get("dependency_health", 0.5))

            X = np.array(X)
            y_quality = np.array(y_quality)
            y_security = np.array(y_security)
            y_maintenance = np.array(y_maintenance)
            y_popularity = np.array(y_popularity)
            y_dependency = np.array(y_dependency)

            # Split data
            X_train, X_test, y_quality_train, y_quality_test = train_test_split(
                X, y_quality, test_size=0.2, random_state=42
            )

            # Train quality model
            self.quality_model = RandomForestRegressor(
                n_estimators=100, random_state=42
            )
            self.quality_model.fit(X_train, y_quality_train)

            # Train security model
            self.security_model = RandomForestClassifier(
                n_estimators=100, random_state=42
            )
            self.security_model.fit(X_train, y_security)

            # Train maintenance model
            self.maintenance_model = RandomForestRegressor(
                n_estimators=100, random_state=42
            )
            self.maintenance_model.fit(X_train, y_maintenance)

            # Train popularity model
            self.popularity_model = RandomForestClassifier(
                n_estimators=100, random_state=42
            )
            self.popularity_model.fit(X_train, y_popularity)

            # Train dependency model
            self.dependency_model = RandomForestRegressor(
                n_estimators=100, random_state=42
            )
            self.dependency_model.fit(X_train, y_dependency)

            # Save models
            self._save_models()

            # Evaluate models
            self._evaluate_models(
                X_test,
                y_quality_test,
                y_security,
                y_maintenance,
                y_popularity,
                y_dependency,
            )

        except Exception as e:
            self.logger.error(f"Model training failed: {e}")

    def _save_models(self) -> None:
        """Save trained models to disk."""
        try:
            models = {
                "quality_model.pkl": self.quality_model,
                "security_model.pkl": self.security_model,
                "maintenance_model.pkl": self.maintenance_model,
                "popularity_model.pkl": self.popularity_model,
                "dependency_model.pkl": self.dependency_model,
                "text_vectorizer.pkl": self.text_vectorizer,
                "feature_scaler.pkl": self.scaler,
            }

            for filename, model in models.items():
                if model is not None:
                    model_file = self.model_dir / filename
                    with open(model_file, "wb") as f:
                        pickle.dump(model, f)

            # Save metadata
            metadata = {
                "version": self.model_version,
                "feature_names": self.feature_names,
                "model_count": len([m for m in models.values() if m is not None]),
            }

            metadata_file = self.model_dir / "model_metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            self.logger.info("Models saved successfully")

        except Exception as e:
            self.logger.error(f"Failed to save models: {e}")

    def _evaluate_models(
        self,
        X_test: np.ndarray,
        y_quality_test: np.ndarray,
        y_security: np.ndarray,
        y_maintenance: np.ndarray,
        y_popularity: np.ndarray,
        y_dependency: np.ndarray,
    ) -> None:
        """Evaluate model performance."""
        try:
            if self.quality_model is not None:
                y_pred = self.quality_model.predict(X_test)
                mse = mean_squared_error(y_quality_test, y_pred)
                self.logger.info(f"Quality model MSE: {mse:.4f}")

            if self.security_model is not None:
                y_pred = self.security_model.predict(X_test)
                report = classification_report(
                    y_security, y_pred, target_names=["low", "medium", "high"]
                )
                self.logger.info(f"Security model report:\n{report}")

        except Exception as e:
            self.logger.warning(f"Model evaluation failed: {e}")


# Global predictor instance
_global_predictor: Optional[CrateQualityPredictor] = None


def get_predictor() -> CrateQualityPredictor:
    """Get global predictor instance."""
    global _global_predictor
    if _global_predictor is None:
        _global_predictor = CrateQualityPredictor()
    return _global_predictor


def set_predictor(predictor: CrateQualityPredictor) -> None:
    """Set global predictor instance."""
    global _global_predictor
    _global_predictor = predictor
