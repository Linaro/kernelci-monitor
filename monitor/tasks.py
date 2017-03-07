# Copyright (C) 2017 Linaro Limited
#
# Author: Milosz Wasilewski <milosz.wasilewski@linaro.org>
#
# This file is part of KernelCI-monitor.
#
# KernelCI-monitor is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# KernelCI-monitor in distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with KernelCI-monitor.  If not, see <http://www.gnu.org/licenses/>.

import logging
import pytz
import requests
import yaml

from datetime import datetime, timedelta
from string import Template

from django.conf import settings
from django.utils import timezone

from kernelcimonitor import celery_app
from monitor.kernelci import kernelci
from monitor.models import Board, KernelCIJob, TestTemplate, SeenBuild

logger = logging.getLogger("tasks")

try:
    # try python3 first
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

try:
    from urllib.parse import urljoin, urlsplit
except ImportError:
    # Python 2
    from urlparse import urljoin, urlsplit

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1


class LAVADefinitionException(Exception):
    pass

class LAVAResponseException(Exception):
    pass

class LAVADefinition(object):

    def __init__(self):
        self.device_type = None
        self.job_name = None
        self.timeouts = {
            'job': {'minutes': 15},
            'action': {'minutes': 5},
            'connection': {'minutes': 2}
        }
        self.priority = 'medium'
        self.visibility = 'public'
        self.actions = []

    def prepare_job_definition(self):
        if self.device_type is None:
            raise LAVADefinitionException("Device Type not set")
        if self.job_name is None:
            raise LAVADefinitionException("Job Name not set")
        if not self.actions:
            raise LAVADefinitionException("No actions defined")
        # maybe return yaml ?
        return self.__dict__

    def add_action(self, action):
        """
        Adds action in the form of (python dictionary)
        boot:
          method: u-boot
          prompts:
            - 'root@linaro-nano:'
        ...
        """
        logger.debug(action)
        # check if action is valid
        # check if action is a dictionary
        if type(action) is not dict:
            raise LAVADefinitionException("Incorrect action - wrong type")
        # check if main dict key is in the list
        if len(action.keys()) != 1:
            raise LAVADefinitionException("Incorrect action - incorrect structure")
        for key in action.keys():
            if key in ['deploy', 'boot', 'test']:
                continue
            raise LAVADefinitionException("Incorrect action - invalid main key")
        # won't check more details. LAVA will validate upon submission
        self.actions.append(action)


def _get_build(build_id):
    builds = kernelci("build", _id=build_id, field="dirname")['result']
    if builds and len(builds) == 1:
        return builds[0] # there should be only one
    return []

@celery_app.task(bind=True)
def monitor_boots(self):
    boards = Board.objects.filter(enabled=True)
    jobs = KernelCIJob.objects.filter(enabled=True)

    # TODO: do we want to check all boards for all jobs?
    # TODO: is there a better way of querying (list multiple boards?)
    for job in jobs:
        for board in boards:
            fetch_boots(job, board)


def fetch_boots(job, board):
    for defconfig in board.defconfigs:
        results_res = kernelci(
            "boot",
            date_range=settings.KERNELCI_DATE_RANGE,
            job=job.name,
            git_branch=job.branch,
            board=board.kernelciname,
            defconfig_full=defconfig,
            status='PASS')
        if not 'result' in results_res.keys():
            logger.warning("Result not found in response")
            logger.warning(results_res)
            return
        results = results_res['result']
        for result in results:
            kernelci_pull.delay(job.id, board.id, result)


@celery_app.task(bind=True)
def kernelci_pull(self, kernelcijob_id, kernelciboard_id, boot):
    kernelcijob = KernelCIJob.objects.get(pk=kernelcijob_id)
    kernelciboard = Board.objects.get(pk=kernelciboard_id)

    logger.debug(boot)
    build_id = boot['build_id']['$oid']
    build = _get_build(build_id)
    boot_id = boot['_id']['$oid']
    board = boot['board']
    dtb = boot['dtb']
    timestamp = datetime.fromtimestamp(boot['created_on']['$date'] / 1000)
    created_at = timezone.make_aware(timestamp, pytz.UTC)

    tree = boot['job']
    branch = boot['git_branch']
    commit = boot['git_commit']
    kernel = boot['kernel']
    defconfig = boot['defconfig_full']
    arch = boot['arch']
    job = boot['job']

    directory = "/var/www/images/kernel-ci/"

    dtb_url = urljoin(settings.KERNELCI_STORAGE_URL,
                      "%s/%s" % (build['dirname'].replace(directory, ""),
                                 dtb))

    image_url = urljoin(settings.KERNELCI_STORAGE_URL,
                        "%s/%s" % (build['dirname'].replace(directory, ""),
                                   boot['kernel_image']))

    kernelci_boot_url = urljoin(settings.KERNELCI_URL, "boot/id/%s" % (boot_id))
    kernelci_build_url = urljoin(settings.KERNELCI_URL, "build/id/%s" % (build_id))
    logger.info((build_id, board, tree, branch, kernel, defconfig, arch, dtb_url, image_url))
    metadata = {
        'build_id': build_id,
        'boot_id': boot_id,
        'board': board,
        'job': kernelcijob,
        'tree': tree,
        'branch': branch,
        'commit': commit,
        'kernel': kernel,
        'defconfig': defconfig,
        'arch': arch,
        'dtb_url': dtb_url,
        'image_url': image_url,
        'kernelci_build_url': kernelci_build_url,
        'kernelci_boot_url': kernelci_boot_url
    }
    logger.debug("creating test job with the following parameters:")
    logger.debug(kernelciboard)
    logger.debug(yaml.dump(metadata, default_flow_style=False))
    # comment for testing
    testjobs_automatic_create.delay(kernelciboard.id, metadata)
    # uncomment for testing
    #testjobs_automatic_create.run(kernelciboard, metadata)


def _create_test_template(board, test, metadata):
    lava_definition = LAVADefinition()
    lava_definition.device_type = board.lavaname
    lava_definition.job_name = "%s-%s-%s" % (metadata['kernel'], board.kernelciname, test.name)
    deploy_str = Template(board.deploytemplate)
    #deploy_str.substitute(metadata)
    deploy = yaml.load(deploy_str.substitute(metadata))
    lava_definition.add_action(deploy)
    boot_str = Template(board.boottemplate)
    #boot_str.substitute(metadata)
    boot = yaml.load(boot_str.substitute(metadata))
    lava_definition.add_action(boot)
    lava_definition.add_action(test.lava_template())
    return lava_definition.prepare_job_definition()


def _call_xmlrpc(method_name, *method_params):
    payload = xmlrpclib.dumps((method_params), method_name)

    logger.debug(settings.LAVA_XMLRPC_URL)
    response = requests.request('POST', settings.LAVA_XMLRPC_URL,
                                data = payload,
                                headers = {'Content-Type': 'application/xml'},
                                auth = (settings.LAVA_USERNAME, settings.LAVA_PASSWORD),
                                timeout = 100,
                                stream = False)

    if response.status_code == 200:
        try:
            result = xmlrpclib.loads(response.content)[0][0]
            return result
        except xmlrpclib.Fault as e:
            message = "Fault code: %d, Fault string: %s\n %s" % (
                e.faultCode, e.faultString, payload)
            raise LAVAResponseException(message)
    else:
        raise LAVAServerException(settings.LAVA_XMLRPC_URL, response.status_code)


def _submit_to_lava(testjobtemplate):
    logger.debug(yaml.dump(testjobtemplate, default_flow_style=False))
    lava_job_id = _call_xmlrpc("scheduler.submit_job", yaml.dump(testjobtemplate, default_flow_style=False))
    return lava_job_id


def _notify_squadlistener(testjob, metadata):
    squad_project = "%s/%s" % (metadata['job'].squad_project_name, metadata['commit'])
    lava_server = urlsplit(settings.LAVA_XMLRPC_URL)
    headers = {"Authorization": "Token %s" % settings.SQUADLISTENER_TOKEN}
    logger.debug("lava_server %s://%s" % (lava_server.scheme, lava_server.netloc))
    logger.debug("lava_job_id %s" % testjob)
    logger.debug("build_job_name %s" % squad_project)
    logger.debug("build_job_url %s" % metadata['kernelci_build_url'])
    r = requests.post(settings.SQUADLISTENER_API_URL,
                      headers=headers,
                      json={"lava_server": "%s://%s" % (lava_server.scheme, lava_server.netloc),
                            "lava_job_id": testjob,
                            "build_job_name": squad_project,
                            "build_job_url": metadata['kernelci_build_url']})


@celery_app.task(bind=True)
def testjobs_automatic_create(self, board_id, metadata):
    board = Board.objects.get(pk=board_id)

    if SeenBuild.objects.filter(board=board, gitcommit=metadata['commit']).exists():
        return

    for test in TestTemplate.objects.all():
        testjobtemplate = _create_test_template(board, test, metadata)
        test_job_id = _submit_to_lava(testjobtemplate)
        _notify_squadlistener(test_job_id, metadata)

        SeenBuild.objects.create(board=board, gitcommit=metadata['commit'])
        logger.info("TestJob %s deployed" % (test_job_id))

