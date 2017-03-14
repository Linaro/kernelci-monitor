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
# KernelCI-monitor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with KernelCI-monitor. If not, see <http://www.gnu.org/licenses/>.

import yaml

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_yaml(value):
    try:
        yaml.load(value)
    except Exception as err:
        raise ValidationError(
            _('Not a valid YAML.\n%(err)s'),
            params={'err': err},
        )


class KernelCIJob(models.Model):
    enabled = models.BooleanField(default=True)
    name = models.CharField(max_length=64)
    branch = models.CharField(max_length=128)
    squad_project_name = models.CharField(max_length=128)

    def __str__(self):
        return "%s (%s)" % (self.name, self.branch)


class Board(models.Model):
    enabled = models.BooleanField(default=True)
    kernelciname = models.CharField(max_length=64)
    lavaname = models.CharField(max_length=64)
    defconfiglist = models.CharField(max_length=1024, default='', blank=True)
    ARM = 'arm'
    ARM64 = 'arm64'
    X86 = 'x86'
    ARCH_CHOICES = (
        (ARM, ARM),
        (ARM64, ARM64),
        (X86, X86)
    )
    arch = models.CharField(
        max_length=8,
        choices=ARCH_CHOICES,
        default=ARM64
    )
    deploytemplate = models.TextField(null=True, blank=True, validators=[validate_yaml])
    boottemplate = models.TextField(null=True, blank=True, validators=[validate_yaml])

    def __str__(self):
        return "%s (%s)" % (self.kernelciname, self.arch)

    @property
    def defconfigs(self):
        return self.defconfiglist.split()


class LastChecked(models.Model):
    kernelcijob = models.ForeignKey(KernelCIJob)
    kernelciboard = models.ForeignKey(Board)
    last_update = models.DateTimeField(auto_now=True)


class TestTemplate(models.Model):
    name = models.CharField(max_length=32)
    gitrepo = models.CharField(max_length=1024)
    testname = models.CharField(max_length=1024)
    parameters = models.CharField(max_length=1024, blank=True, null=True)

    def __str__(self):
        return self.name

    def lava_template(self):
        test_dict = {
            "timeout": {"minutes": 30},
            "definitions": [
                {
                    "from": "git",
                    "repository": self.gitrepo,
                    "path": self.testname,
                    "name": self.name
                }
            ]
        }
        # add timeout
        # add parameters

        return {"test": test_dict}


class SeenBuild(models.Model):
    # git will eventually move away from SHA1, so 40 is not enough
    gitcommit = models.CharField(max_length=128)
    board = models.ForeignKey(Board, related_name='seen_builds')

    class Meta:
        unique_together = ('board', 'gitcommit')
