import os
from typing import Optional
from multiprocessing import Process, JoinableQueue

from behave.model import Feature
from behave.configuration import Configuration

from . import Worker


class ProcessWorker(Worker):
    """Реализация воркера на основе отдельного процесса (multiprocessing)

    Основные функции:
    - Выполнение фичей в изолированном процессе
    - Использование очереди задач для управления выполнением
    - Поддержка дочерних процессов с возможностью завершения
    """

    _process: Process
    _task_queue: JoinableQueue

    def __init__(self, config: Configuration, index: int):
        """Инициализация воркера с новым процессом

        Args:
            config: Конфигурация из behave
            index: Индекс воркера
        """
        super().__init__(config, index)
        self._process = Process(
            target=self._process_loop,
            args=(os.environ,),  # Передаем текущие переменные окружения
            name=str(self),
            daemon=True,  # Демон-процесс завершится при выходе из основного
        )
        self._task_queue = JoinableQueue()
        self._process.start()

    def run_feature(self, feature: Optional[Feature]) -> None:
        """Добавить фичу в очередь задач

        Args:
            feature: Объект Feature для выполнения или None для завершения
        """
        self._task_queue.put_nowait(feature)

    def done(self) -> bool:
        """Проверить завершение работы процесса

        Returns:
            True, если процесс завершил работу или очередь пуста
        """
        return (
            not self._process.is_alive()  #
            or self._task_queue._unfinished_tasks._semlock._is_zero()
        )

    def shutdown(self):
        """Завершить работу воркера

        Отправляет сигнал остановки и ожидает завершения процесса
        """
        if self._process.is_alive():
            self._task_queue.put(None)  # Сигнал завершения
            while not self.done():
                pass
            self._process.terminate()
            self._process.join()
        self._task_queue.close()

    def _process_loop(self, envs):
        """Цикл работы процесса

        Инициализирует окружение и выполняет задачи из очереди

        Args:
            envs: Переменные окружения родительского процесса
        """
        os.environ = envs

        self.runner.config.setup_formats()

        while True:
            feature = self._task_queue.get()

            self.runner.run_feature(feature)
            self._task_queue.task_done()

            if self.runner._is_finished:
                break
