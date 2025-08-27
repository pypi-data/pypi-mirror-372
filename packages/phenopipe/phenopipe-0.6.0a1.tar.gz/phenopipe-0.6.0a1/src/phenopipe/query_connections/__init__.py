from .big_query_connection import BigQueryConnection

__all__ = ["BigQueryConnection"]

import importlib

databrics_extras = importlib.util.find_spec("databricks")
if databrics_extras is not None:
    from .databricks_query_connection import DatabricksQueryConnection

    __all__ = __all__ + ["DatabricksQueryConnection"]
