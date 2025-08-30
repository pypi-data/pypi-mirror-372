"""MAIS application configuration using pydantic-settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MAISConfig(BaseSettings):
    """Central configuration for MAIS application.

    Configuration can be set via:
    1. Environment variables (with MAIS_ prefix)
    2. .env file
    3. Direct instantiation
    """

    # API Configuration
    mosaic_api_url: str = Field(
        default="https://api.manifestcyber.com",
        description="MOSAIC API base URL",
    )
    api_timeout: int = Field(
        default=30, description="API request timeout in seconds"
    )
    manifest_api_token: str | None = Field(
        default=None, description="API token for authentication"
    )

    # Model Detection Configuration
    watched_functions: list[str] = Field(
        default=[
            "torch.load",
            "torch.hub.load",
            "joblib.load",
            "pickle.load",
            "pickle.loads",
            "dill.load",
            "dill.loads",
            "numpy.load",
            "transformers.AutoModel.from_pretrained",
            "transformers.AutoModelForCausalLM.from_pretrained",
            "transformers.AutoModelForSequenceClassification.from_pretrained",
            "transformers.AutoTokenizer.from_pretrained",
            "transformers.pipeline",
            "keras.models.load_model",
            "tensorflow.keras.models.load_model",
            "sklearn.externals.joblib.load",
            "transformers.Trainer",
        ],
        description="Functions to watch for model loading, training, datasets, etc.",
    )

    watched_classes: list[str] = Field(
        default=[
            "AutoModel",
            "AutoModelForSequenceClassification",
            "AutoTokenizer",
            "pipeline",
            "Trainer",
        ],
        description="Classes to watch for model loading",
    )

    model_related_kwargs: list[str] = Field(
        default=["model", "model_name", "pretrained_model_name_or_path"],
        description="Keyword arguments related to model loading",
    )

    # Logging Configuration
    default_verbosity: str = Field(
        default="WARNING", description="Default logging level"
    )

    # SBOM Configuration
    sbom_timeout: int = Field(
        default=60, description="SBOM generation timeout in seconds"
    )

    # Feature Flags
    mosaic_enabled: bool = Field(
        default=True, description="Enable MOSAIC API integration"
    )

    model_config = SettingsConfigDict(
        env_prefix="MAIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",  # Allow extra fields for forward compatibility
    )

    datasets_tasks: dict[str, str] = Field(
        default={
            # NLP Tasks
            "text-classification": "Text Classification",
            "token-classification": "Token Classification",
            "question-answering": "Question Answering",
            "table-question-answering": "Table Question Answering",
            "zero-shot-classification": "Zero-Shot Classification",
            "translation": "Translation",
            "summarization": "Summarization",
            "feature-extraction": "Feature Extraction",
            "text-generation": "Text Generation",
            "fill-mask": "Fill-Mask",
            "sentence-similarity": "Sentence Similarity",
            "table-to-text": "Table to Text",
            "multiple-choice": "Multiple Choice",
            "text-ranking": "Text Ranking",
            "text-retrieval": "Text Retrieval",
            # Computer Vision Tasks
            "image-classification": "Image Classification",
            "object-detection": "Object Detection",
            "image-segmentation": "Image Segmentation",
            "depth-estimation": "Depth Estimation",
            "zero-shot-image-classification": "Zero-Shot Image Classification",
            "mask-generation": "Mask Generation",
            "zero-shot-object-detection": "Zero-Shot Object Detection",
            "image-feature-extraction": "Image Feature Extraction",
            "image-to-image": "Image-to-Image",
            "image-to-text": "Image-to-Text",
            "text-to-image": "Text-to-Image",
            "image-to-video": "Image-to-Video",
            "unconditional-image-generation": "Unconditional Image Generation",
            "visual-question-answering": "Visual Question Answering",
            "visual-document-retrieval": "Visual Document Retrieval",
            "image-to-3d": "Image-to-3D",
            "text-to-3d": "Text-to-3D",
            # Video Tasks
            "video-classification": "Video Classification",
            "text-to-video": "Text-to-Video",
            "video-text-to-text": "Video-Text-to-Text",
            # Audio Tasks
            "audio-classification": "Audio Classification",
            "automatic-speech-recognition": "Automatic Speech Recognition",
            "voice-activity-detection": "Voice Activity Detection",
            "audio-to-audio": "Audio-to-Audio",
            "text-to-speech": "Text-to-Speech",
            "text-to-audio": "Text-to-Audio",
            # Tabular & Time Series
            "tabular-classification": "Tabular Classification",
            "tabular-regression": "Tabular Regression",
            "tabular-to-text": "Tabular to Text",
            "time-series-forecasting": "Time Series Forecasting",
            # Reinforcement Learning & Robotics
            "reinforcement-learning": "Reinforcement Learning",
            "robotics": "Robotics",
            # Graphs
            "graph-machine-learning": "Graph Machine Learning",
            # Multi-modal/Other
            "any-to-any": "Any-to-Any",
            "computer-vision": "Computer Vision",
            "natural-language-processing": "Natural Language Processing",
            "audio": "Audio",
            "other": "Other",
        },
        description="Mapping of datasets tasks to human-readable names",
    )

    finetuning_functions: list[str] = Field(
        default=[
            "transformers.Trainer",
            "Trainer",
        ],
        description="Functions/classes that indicate fine-tuning and should trigger base model setting",
    )

    finetuning_classes: list[str] = Field(
        default=[
            "Trainer",
        ],
        description="Classes that indicate fine-tuning and should trigger base model setting",
    )


# Global config instance
_config: MAISConfig | None = None


def get_config() -> MAISConfig:
    """Get or create the global configuration instance.

    Returns:
        MAISConfig: The configuration instance
    """
    global _config
    if _config is None:
        _config = MAISConfig()
    return _config


def set_config(config: MAISConfig) -> None:
    """Set the global configuration instance.

    Args:
        config: The configuration instance to use
    """
    global _config
    _config = config
