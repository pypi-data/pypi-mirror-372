from adaptive_harmony import TrainingModel
from datetime import datetime
from loguru import logger


async def save_model_safely(training_model: TrainingModel, model_key: str):
    """
    Safely save a model, automatically adding a timestamp suffix if the model already exists.
    """
    original_name = model_key

    try:
        await training_model.save(model_key)
        logger.info(f"✓ Model '{model_key}' saved successfully")
        return model_key
    except RuntimeError as e:
        error_msg = str(e)

        # Check if this is a ModelOverwriteError
        if "ModelOverwriteError" in error_msg:
            logger.warning(f"⚠️  Model '{model_key}' already exists, adding timestamp suffix...")

            # Generate timestamp in format that won't be changed by slugification
            # Using YYYY-MM-DD-THHMMSS format (no colons, spaces, or special chars)
            timestamp = datetime.now().strftime("%Y-%m-%d-T%H-%M-%S")
            timestamped_name = f"{original_name}-{timestamp}"

            try:
                await training_model.save(timestamped_name)
                logger.info(f"✓ Model saved as '{timestamped_name}' with timestamp suffix")
                return timestamped_name
            except RuntimeError as e2:
                # If even the timestamped version fails, something else is wrong
                logger.error(f"❌ Failed to save even with timestamp suffix: {e2}")
                raise
        else:
            # Some other RuntimeError occurred - re-raise it
            logger.error(f"❌ Unexpected error saving model '{model_key}': {error_msg}")
            raise
