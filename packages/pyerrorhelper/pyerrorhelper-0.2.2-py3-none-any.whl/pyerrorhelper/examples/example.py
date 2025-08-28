from pyerrorhelper import ErrorManager

if __name__ == "__main__":
    error_manager = ErrorManager()
    error_manager.install()

    # Example to trigger an exception
    def cause_error() -> float:
        return 1 / 0  # This will raise a ZeroDivisionError

    cause_error()

    error_manager.uninstall()
