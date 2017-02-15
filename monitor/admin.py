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

from django.contrib import admin
from monitor.models import *


class KernelCIJobAdmin(admin.ModelAdmin):
    pass


class BoardAdmin(admin.ModelAdmin):
    pass


class TestTemplateAdmin(admin.ModelAdmin):
    pass


admin.site.register(KernelCIJob, KernelCIJobAdmin)
admin.site.register(Board, BoardAdmin)
admin.site.register(TestTemplate, TestTemplateAdmin)
