"""
Created on 2025-05-28

@author: wf
"""

from basemkit.basetest import Basetest
from basemkit.docker_util import DockerUtil
from basemkit.persistent_log import Log
from basemkit.shell import Shell


class TestDockerUtil(Basetest):
    """
    test docker utilities
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.shell = Shell()
        self.log = Log()
        self.container_name = "test_container"
        self.docker_util = DockerUtil(self.shell, self.container_name, log=self.log, debug=debug)

    def test_initialization(self):
        """
        test DockerUtil initialization
        """
        self.assertEqual(self.docker_util.container_name, "test_container")
        self.assertIsNotNone(self.docker_util.shell)
        self.assertFalse(self.docker_util.debug)
