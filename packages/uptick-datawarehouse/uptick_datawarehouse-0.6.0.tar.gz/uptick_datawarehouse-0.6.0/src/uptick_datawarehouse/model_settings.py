import os

# We need to be able to swap a model from being managed/unmanaged if it is being imported or not
DATAWAREHOUSE_MANAGED_MODELS = bool(
    os.environ.get("DATAWAREHOUSE_MANAGED_MODELS", False)
)
