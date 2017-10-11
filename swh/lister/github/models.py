# Copyright (C) 2017 the Software Heritage developers
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from sqlalchemy import Column, Boolean, Integer

from swh.lister.core.models import ModelBase


class GitHubModel(ModelBase):
    """a GitHub repository"""
    __tablename__ = 'github_repos'

    uid = Column(Integer, primary_key=True)
    indexable = Column(Integer, index=True)
    fork = Column(Boolean)

    def __init__(self, *args, **kwargs):
        self.fork = kwargs.pop('fork', False)
        super().__init__(*args, **kwargs)
