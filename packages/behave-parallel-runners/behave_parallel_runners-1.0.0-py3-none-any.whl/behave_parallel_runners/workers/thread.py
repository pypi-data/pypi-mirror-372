from typing import Optional
from threading import Thread
from queue import Queue

from behave.model import Feature
from behave.configuration import Configuration

from . import Worker


class ThreadWorker(Worker):
    """Реализация воркера на основе потока (thread)

    Основные функции:
    - Выполнение фичей в отдельном потоке
    - Использование очереди задач для управления выполнением
    - Автоматическое завершение работы при отсутствии задач
    """

    _thread: Thread
    _task_queue: Queue

    def __init__(self, config: Configuration, index: int):
        """Инициализация воркера

        Args:
            config: Конфигурация из behave
            index: Индекс воркера
        """
        super().__init__(config, index)
        self._thread = Thread(
            target=self._thread_loop,
            name=str(self),
            daemon=True,
        )
        self._task_queue = Queue()
        self._thread.start()

    def run_feature(self, feature: Optional[Feature]) -> None:
        """Добавить фичу в очередь задач

        Args:
            feature: Объект Feature для выполнения или None для завершения
        """
        self._task_queue.put_nowait(feature)

    def done(self) -> bool:
        """Проверить завершение работы воркера

        Returns:
            True, если поток завершил работу или очередь пуста
        """
        return not self._thread.is_alive() or self._task_queue.unfinished_tasks == 0

    def shutdown(self):
        """Завершить работу воркера

        Отправляет сигнал остановки и ждет завершения потока
        """
        self.run_feature(None)
        self._thread.join()
        self._task_queue.shutdown()

    def _thread_loop(self):
        """Цикл работы потока

        Постоянно получает задачи из очереди и выполняет их
        """
        while True:
            feature = self._task_queue.get()

            self.runner.run_feature(feature)
            self._task_queue.task_done()

            if self.runner._is_finished:
                break
