from django.test import TestCase
from monitor.models import (
    KernelCIJob,
    Board,
    LastChecked,
    TestTemplate,
    SeenBuild
)

class BoardTest(TestCase):

    def test_defconfig(self):
        board = Board(defconfiglist='foo bar')
        self.assertEqual(['foo', 'bar'], board.defconfigs)


class KernelCIJobTest(TestCase):

    def test_enabled(self):
        job = KernelCIJob(enabled=True, name="foo", branch="bar", squad_project_name="foo/bar")
        self.assertTrue(job.enabled)
        job.enabled = False
        job.save()
        self.assertFalse(job.enabled)


class LastCheckedTest(TestCase):

    def test_last_update(self):
        job = KernelCIJob(enabled=True, name="foo", branch="bar", squad_project_name="foo/bar")
        job.save()
        board = Board(kernelciname="board_foo", lavaname="board_bar", arch="arm")
        board.save()
        lc = LastChecked(kernelcijob=job, kernelciboard=board)
        lc.save()
        last_update = lc.last_update
        lc.save()
        self.assertGreater(lc.last_update, last_update)


class TestTemplateTest(TestCase):

    def test_valid_yaml(self):
        t = TestTemplate(
            name="foo",
            gitrepo="git://git.linaro.org/qa/test-definitions.git",
            testname="automated/linux/smoke/smoke.yaml")
        template = t.lava_template()
        self.assertIsInstance(template, dict)
