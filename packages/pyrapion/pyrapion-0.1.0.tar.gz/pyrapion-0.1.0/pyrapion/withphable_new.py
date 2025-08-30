"""
with phable v1.1.10

some modification
"""
import pandas as pd
from phable.client import Client


class WithPhableClient():
    def __init__(self, uri, user, passwd):
        self.uri = uri
        self.username = user
        self.password = passwd

    def readAll(self, filter_str):
        with Client(self.uri, self.username, self.password) as ph:
            # fetch info about the Haystack server
            point_meta = ph.read(
                filter_str
            )
        if point_meta.empty:
            print("Warning: No data")
        else:
            return point_meta

    def hisRead(self, ids: list, datespan_str: str) -> pd.DataFrame:
        with Client(self.uri, self.username, self.password) as ph:
            # fetch info about the Haystack server
            batch_his_read_df = ph.his_read(
                ids, datespan_str
            )
        if batch_his_read_df.empty:
            print("Warning: no data")
        else:
            batch_his_read_df.index = batch_his_read_df.index.tz_localize(None)
            return batch_his_read_df

    def batch_his_read(
        self,
        filter_str: str,
        datespan_str: str,
        **kwargs
    ):
        """
        filter_str: str
            axon filter
        datespan_str: str
            date span
        """
        with Client(self.uri, self.username, self.password) as ph:
            # fetch info about the Haystack server
            point_meta = ph.read(
                filter_str
            )

            batch_his_read_df = ph.his_read(
                [id for id in point_meta["id"]], datespan_str
                )
        if batch_his_read_df.empty:
            print("Warning: no data")
        else:
            batch_his_read_df.index = batch_his_read_df.index.tz_localize(None)
            return point_meta, batch_his_read_df
