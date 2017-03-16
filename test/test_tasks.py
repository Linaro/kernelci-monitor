from django.test import TestCase, override_settings
from django_dynamic_fixture import G

from unittest.mock import patch

from monitor import tasks
from monitor.models import (
    KernelCIJob,
    Board,
    LastChecked,
    TestTemplate,
    SeenBuild
)
import logging
import sys
logger = logging.getLogger("tasks")
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

GIT_COMMIT = '08819f4ac52f099b866c959b3258b40ffbbbdb74'
mock_reply = {
    'code': 200,
    'count': 1,
    'limit': 50000,
    'result': [{'_id': {'$oid': '58c677c259b5146093645543'},
        'arch': 'arm64',
        'board': 'apm-mustang',
        'board_instance': 'mustang05',
        'boot_job_id': None,
        'boot_job_path': None,
        'boot_job_url': None,
        'boot_log': 'boot-apm-mustang.txt',
        'boot_log_html': 'boot-apm-mustang.html',
        'boot_result_description': None,
        'bootloader': None,
        'bootloader_version': None,
        'build_id': {'$oid': '58c662b959b514504f645538'},
        'chainloader': None,
        'compiler': 'gcc',
        'compiler_version': '5.3.1',
        'compiler_version_ext': 'gcc 5.3.1',
        'compiler_version_full': 'gcc version 5.3.1 20160412 (Linaro GCC '
                                 '5.3-2016.05)',
        'created_on': {'$date': 1489401794713},
        'cross_compile': 'aarch64-linux-gnu-',
        'defconfig': 'defconfig',
        'defconfig_full': 'defconfig',
        'dtb': 'dtbs/apm/apm-mustang.dtb',
        'dtb_addr': '0x4003000000',
        'dtb_append': 'False',
        'endian': 'little',
        'fastboot': 'false',
        'fastboot_cmd': None,
        'file_server_resource': None,
        'file_server_url': None,
        'filesystem': None,
        'git_branch': 'local/linux-4.4.y',
        'git_commit': GIT_COMMIT,
        'git_describe': 'v4.4.53-37-g08819f4ac52f',
        'git_url': 'http://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable-rc.git',
        'initrd': None,
        'initrd_addr': '0x4004000000',
        'job': 'stable-rc',
        'job_id': {'$oid': '58c65d7059b5144d82645532'},
        'kernel': 'v4.4.53-37-g08819f4ac52f',
        'kernel_image': 'Image',
        'kernel_image_size': 9323008,
        'lab_name': 'lab-cambridge',
        'load_addr': '0x00080000',
        'mach': 'apm',
        'metadata': {},
        'qemu': None,
        'qemu_command': None,
        'retries': 0,
        'status': 'PASS',
        'time': {'$date': 6810},
        'uimage': None,
        'uimage_addr': None,
        'version': '1.0',
        'warnings': None}]}
mock_build = {'_id': {'$oid': '58c662b959b514504f645538'},
     'dirname': '/var/www/images/kernel-ci/stable-rc/v4.4.53-37-g08819f4ac52f/arm64-defconfig'}

class TaskTest(TestCase):

    @patch('monitor.tasks.kernelci', return_value=mock_reply)
    @patch('monitor.tasks._submit_to_lava', return_value="12345")
    @patch('monitor.tasks._notify_squadlistener', return_value=True)
    @patch('monitor.tasks._get_build', return_value=mock_build)
    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_monitor_boots(
            self,
            mock_kernelci,
            mock_submit_to_lava,
            mock_notify_squadlistener,
            mock_get_build):

        kernelcijob = G(KernelCIJob)
        board = G(Board)
        board.defconfiglist = "a"
        board.save()

        tasks.monitor_boots()
        self.assertEqual(len(SeenBuild.objects.all()), 1)
        self.assertEqual(SeenBuild.objects.all().first().gitcommit, GIT_COMMIT)
