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
# KernelCI-monitor  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with KernelCI-monitor. If not, see <http://www.gnu.org/licenses/>.

import requests

from django.conf import settings
headers = {"Authorization": settings.KERNELCI_TOKEN}

defaults = {
    "limit": 50000,
    "sort_order": -1,
    "sort": "created_on"
}


def kernelci(handler, **kwargs):

    url = settings.KERNELCI_API_URL % handler

    params = defaults.copy()
    params.update(kwargs)

    response = requests.get(
        url,
        headers=headers,
        params=params
    )
    return response.json()


# for test purposes only. Not in use for the django application
if __name__ == '__main__':
    from pprint import pprint
    job = 'stable-rc'
    arch = 'arm64'
    branch = 'local/linux-4.4.y'
    board = 'apm-mustang'
    r = kernelci("boot", status='PASS', date_range=3, job=job, arch=arch, git_branch=branch, board=board)['result']
    for res in r:
        pprint(res)
        build_res = kernelci("build", _id=res['build_id']['$oid'], field="dirname")
        pprint(build_res)
