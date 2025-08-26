# Copyright (c) 2020 Vemund Halmø Aarstrand
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from multiprocessing import cpu_count

from mjooln import *


class System:
    """
    .. danger:: Experimental class. May change without notice and suddenly disappear

    Convenience methods for system status (cores, memory, disk space)

    """

    @classmethod
    def cores(cls, fraction=None):
        """
        Get number of cores in system

        :param fraction: Fraction of cores to return. If None, total number
            of cores are returned. If, for example, fraction=0.5, half the number of cores
            are returned. Minimum return is 1
        :return: Number of cores available, or a fraction of them
        """
        num_cores = cpu_count()
        if fraction is not None:
            num_cores = round(num_cores * fraction)
            if num_cores < 1:
                num_cores = 1
        return num_cores

    @classmethod
    def current(cls):
        return {
            "memory": cls.memory(),
            "disk": cls.disk_usage(Folder.current()),
        }

    @classmethod
    def memory(cls):
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "percent": mem.percent,
            "used": mem.used,
            "free": mem.free,
        }

    @classmethod
    def disk_usage(cls, folder):
        usage = shutil.disk_usage(str(folder))
        return {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": 100 * usage.used / usage.total,
        }
