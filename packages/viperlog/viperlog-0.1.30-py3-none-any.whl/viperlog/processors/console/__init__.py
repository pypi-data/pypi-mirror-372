try:
    from plugin_viperlog_console import ConsoleProcessor, ConsoleTemplate
except ImportError as err:
    # package not installed, log an error end let it fail later. We could raise the error again but I find it cleaner to just output a message and let it fail in this import instead of the internal
    from logging import getLogger
    #getLogger("viperlog").exception("The ConsoleProcessor is not available because the 'viperlog[console]' package is not installed")
    getLogger("viperlog").error("The ConsoleProcessor is not available because the 'viperlog[console]' or 'viperlog[all]' package is not installed")

