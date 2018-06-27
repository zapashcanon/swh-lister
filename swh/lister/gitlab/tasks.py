# Copyright (C) 2018 the Software Heritage developers
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from swh.lister.core.tasks import (IndexingDiscoveryListerTask,
                                   IndexingRangeListerTask,
                                   IndexingRefreshListerTask, ListerTaskBase)

from .lister import GitlabLister


class GitlabDotComListerTask(ListerTaskBase):
    def new_lister(self):
        return GitlabLister(lister_name='gitlab.com',
                            api_baseurl='https://gitlab.com/api/v4')


class IncrementalGitlabDotComLister(GitlabDotComListerTask,
                                    IndexingDiscoveryListerTask):
    task_queue = 'swh_lister_gitlab_discover'


class RangeGitlabLister(GitlabDotComListerTask, IndexingRangeListerTask):
    task_queue = 'swh_lister_gitlab_refresh'


class FullGitlabRelister(GitlabDotComListerTask, IndexingRefreshListerTask):
    task_queue = 'swh_lister_gitlab_refresh'
