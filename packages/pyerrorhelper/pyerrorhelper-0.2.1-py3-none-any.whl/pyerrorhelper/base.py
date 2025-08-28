class BaseErrorHandler:
    def process_exception(self, type, value, traceback) -> bool:
        return False
