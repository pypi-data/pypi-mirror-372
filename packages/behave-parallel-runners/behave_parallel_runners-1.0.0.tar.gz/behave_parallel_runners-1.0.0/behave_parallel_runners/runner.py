from time import sleep
from behave.configuration import Configuration
from behave.model import Step
from behave.runner import ITestRunner
from behave.runner_util import PathManager

from .task import TaskAllocator
from .workers import WorkerPoolExecutor


class ParallelRunner(ITestRunner):
    """Базовый параллельный исполнитель тестов

    Основные функции:
    - Управление распределением задач между воркерами
    - Параллельное выполнение фичей
    - Сбор результатов выполнения
    """

    config: Configuration
    task_allocator: TaskAllocator
    worker_pool_executor: WorkerPoolExecutor

    def __init__(
        self,
        config: Configuration,
        task_allocator: TaskAllocator,
        worker_pool_executor: WorkerPoolExecutor,
    ):
        """Инициализация параллельного исполнителя

        Args:
            config: Конфигурация из behave
            task_allocator: Распределитель задач
            worker_pool_executor: Пул воркеров
        """
        super().__init__(config)
        self.task_allocator = task_allocator
        self.worker_pool_executor = worker_pool_executor

    def run(self) -> bool:
        """Запуск параллельного выполнения тестов

        Returns:
            True, если произошли ошибки, иначе False
        """
        with PathManager():
            with self.worker_pool_executor as pool:
                # Основной цикл выполнения
                while not (self.task_allocator.empty() and pool.done()):
                    for index, worker in enumerate(pool):
                        if worker.done():
                            # Назначаем новую задачу готовому воркеру
                            feature = self.task_allocator.allocate(index)
                            worker.run_feature(feature)
                    # Минимальная пауза для предотвращения перегрузки CPU
                    sleep(0.05)
            # Проверяем наличие ошибок во всех воркерах
            return any(worker.runner.is_failed for worker in self.worker_pool_executor)

    @property
    def undefined_steps(self) -> list[Step]:
        """Собрать все неопределенные шаги из всех воркеров"""
        return [
            step
            for worker in self.worker_pool_executor
            for step in worker.runner.undefined_steps
        ]
