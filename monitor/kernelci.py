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
    job = 'lsk'
    arch = 'arm'
    branch = 'local/linux-linaro-lsk-v4.4'
    r = kernelci("build", date_range=10, job=job, arch=arch, git_branch=branch)['result']
    for res in r:
        print (res['git_branch'])
