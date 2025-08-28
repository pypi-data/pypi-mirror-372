import asyncio
import dask.dataframe as dd


def is_dask_dataframe(df):
    """Check if the given object is a Dask DataFrame."""
    return isinstance(df, dd.DataFrame)

async def to_thread(func, *args, **kwargs):
    """Explicit helper to keep code clear where we hop off the event loop."""
    return await asyncio.to_thread(func, *args, **kwargs)

