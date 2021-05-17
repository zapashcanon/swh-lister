# Copyright (C) 2021  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import io
import logging
import os
from subprocess import PIPE, Popen
import tempfile
from typing import Iterator

from swh.lister.pattern import StatelessLister
from swh.scheduler.interface import SchedulerInterface
from swh.scheduler.model import ListedOrigin

from ..pattern import CredentialsType

logger = logging.getLogger(__name__)

PageType = str


class OpamLister(StatelessLister[PageType]):
    """
    List all repositories hosted on an opam repository.

    Args:
        url: base URL of an opam repository
            (for instance https://opam.ocaml.org)
        instance: string identifier for the listed repository

    """

    # Part of the lister API, that identifies this lister
    LISTER_NAME = "opam"

    def __init__(
        self,
        scheduler: SchedulerInterface,
        url: str,
        instance: str,
        credentials: CredentialsType = None,
    ):
        super().__init__(
            scheduler=scheduler, credentials=credentials, url=url, instance=instance,
        )
        self.opamroot_path: str = tempfile.mkdtemp()
        self.env = os.environ.copy()
        self.env["OPAMROOT"] = self.opamroot_path
        Popen(
            ["opam", "init", "--reinit", "--bare", "--no-setup", instance, url],
            env=self.env,
        )

    def get_pages(self) -> Iterator[PageType]:
        proc = Popen(
            [
                "opam",
                "list",
                "--all",
                "--no-switch",
                "--repos",
                self.instance,
                "--normalise",
                "--short",
            ],
            env=self.env,
            stdout=PIPE,
        )
        if proc.stdout is not None:
            for line in io.TextIOWrapper(proc.stdout):
                yield line.rstrip("\n")

    def get_origins_from_page(self, page: PageType) -> Iterator[ListedOrigin]:
        """Convert a page of OpamLister repositories into a list of ListedOrigins"""
        assert self.lister_obj.id is not None
        # a page is just a package name
        url = f"opam+{self.url}/packages/{page}/"
        # print("adding url", url)
        yield ListedOrigin(
            lister_id=self.lister_obj.id, visit_type="opam", url=url, last_update=None
        )
