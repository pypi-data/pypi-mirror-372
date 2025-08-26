# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(r'../'))

from hagworm.extend.asyncio.base import Utils
from hagworm.frame.stress_tests import Launcher, RunnerAbstract, TimerMS


class Runner(RunnerAbstract):

    async def _execute(self):

        for index in range(5):

            for _ in range(5):

                with TimerMS() as timer:
                    await Utils.sleep(Utils.randint(10, 99) / 1000)

                if Utils.rand_hit([True, False], [50, 50]):
                    await self.success(f'Test{index}', timer.value)
                else:
                    await self.failure(f'Test{index}', timer.value)


if __name__ == r'__main__':

    Launcher(Runner.create, 5).run()
