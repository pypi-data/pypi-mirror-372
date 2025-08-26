import os
import pandas as pd
import random

import pandas as pd
from importlib import resources

class CommentGenerator:
    def __init__(self, path=None):
        if path is None:
            # This will get the CSV inside the installed package
            with resources.path("comments_generator.data", "dataset.csv") as csv_file:
                path = csv_file
        self.df = pd.read_csv(path)

    def get_random_comment(self, category=None, language=None, tone=None):
        df = self.df
        if category:
            df = df[df["category"] == category]
        if language:
            df = df[df["language"] == language]
        if tone:
            df = df[df["tone"] == tone]

        if df.empty:
            return None
        return df.sample(1).iloc[0]["text"]

    def get_many_comments(self, n=5, **filters):
        return [self.get_random_comment(**filters) for _ in range(n)]
