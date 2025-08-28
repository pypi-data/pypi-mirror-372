import sys

from . import Worker


if sys.version_info >= (3, 14):

    from typing import Optional
    from concurrent.interpreters import create, Interpreter

    from behave.model import Feature
    from behave.configuration import Configuration

    class InterpreterWorker(Worker):
        """Реализация воркера на основе отдельного интерпретатора Python

        Основные функции:
        - Использование нескольких независимых интерпретаторов Python (начиная с версии 3.14)
        - Выполнение фичей в изолированном окружении
        - Асинхронное выполнение без блокировки основного потока
        """

        _interpreter: Interpreter

        def __init__(self, config: Configuration, index: int):
            """Инициализация воркера с новым интерпретатором

            Args:
                config: Конфигурация из behave
                index: Индекс воркера
            """
            super().__init__(config, index)
            self._interpreter = create()

        def run_feature(self, feature: Optional[Feature]) -> None:
            """Выполнить фичу в отдельном интерпретаторе

            Args:
                feature: Объект Feature для выполнения или None для завершения
            """
            self._interpreter.call(self.runner.run_feature, feature)

        def done(self) -> bool:
            """Проверить завершение работы интерпретатора

            Returns:
                True, если интерпретатор завершил работу
            """
            return not self._interpreter.is_running()

        def shutdown(self) -> None:
            """Завершить работу воркера

            Отправляет сигнал остановки и ожидает завершения интерпретатора
            """
            self.run_feature(None)
            while not self.done():
                pass  # Ждем завершения
            self._interpreter.close()

else:

    class InterpreterWorker(Worker):
        """Фиктивный класс для совместимости с версиями Python < 3.14"""

        def __init__(self, config, index):
            """Генерирует ошибку при попытке создания воркера"""
            raise ImportError("InterpreterWorker требует Python >= 3.14")
