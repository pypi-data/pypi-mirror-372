import os

from behave.configuration import Configuration
from behave.runner import ITestRunner

from behave_parallel_runners.runner import ParallelRunner
from behave_parallel_runners.task import (
    FeatureTaskAllocator,
    ScenarioTaskAllocator,
    DirectoryTaskAllocator,
)
from behave_parallel_runners.workers import WorkerPoolExecutor
from behave_parallel_runners.workers.process import ProcessWorker

from zapp.run import configure_runtime


class ZappProcessWorker(ProcessWorker):

    def _process_loop(self, envs):
        os.environ = envs

        configure_runtime()  # Относительно исходного воркера добавляем доп настройку окружения

        self.runner.config.setup_formats()
        while True:
            feature = self._task_queue.get()

            self.runner.run_feature(feature)
            self._task_queue.task_done()

            if self.runner._is_finished:
                break


class FeatureParallelRunner(ParallelRunner):
    def __init__(self, config: Configuration):
        super().__init__(
            config=config,
            task_allocator=FeatureTaskAllocator(config),
            worker_pool_executor=WorkerPoolExecutor(config, ZappProcessWorker),
        )


class ScenarioParallelRunner(ParallelRunner):
    def __init__(self, config: Configuration):
        super().__init__(
            config=config,
            task_allocator=ScenarioTaskAllocator(config),
            worker_pool_executor=WorkerPoolExecutor(config, ZappProcessWorker),
        )


class DirectoryParallelRunner(ParallelRunner):
    def __init__(self, config: Configuration):
        super().__init__(
            config=config,
            task_allocator=DirectoryTaskAllocator(config),
            worker_pool_executor=WorkerPoolExecutor(config, ZappProcessWorker),
        )


ITestRunner.register(FeatureParallelRunner)
ITestRunner.register(ScenarioParallelRunner)
ITestRunner.register(DirectoryParallelRunner)
