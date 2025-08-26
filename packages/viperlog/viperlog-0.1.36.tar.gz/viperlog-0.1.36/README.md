# VIPERLOG

This library is build on top of the python logging, 
it's not meant to replace it but rather make it easier to configure
and work together with it.  

This means that you can still use the build-in python getLogger for logging and no code changes are required apart from configuring this library.

## Installation
Some of the processors like console and http have additional dependencies
and are optionally installed. 

    pip install viperlog[all] # everything
    pip install viperlog[core] # The minimal core module which allows logging to file
    pip install viperlog[console] # console module
    pip install viperlog[http] # http module
    pip install viperlog[console,http] # http+console modules




## Usage

Get an instance of the Viperlog singleton class
    
    # both viperlog.logger.getLogger and logging.getLogger work the same
    import logging
    from viperlog import Viperlog
    from viperlog.processors.console import ConsoleProcessor
    from viperlog.processors import FileProcessor
    from viperlog.formatters import JsonObjectFormatter
    
    # get a logger (normally this is the root logger, but you can attach the handlers any logger)
    logger = logging.getLogger()
    manager = Viperlog()
    
    handler = manager.setup_handler("core-handler", 
                      logger=logger, 
                      min_level=logging.DEBUG, 
                      flush_level=logging.ERROR, 
                      processors=[
                         ConsoleProcessor(
                            template="MyLog: ${datetime} ${level|upper} ${message}"
                         ),
                         FileProcessor(file="/var/log/mylog.txt"),
                         FileProcessor(
                              file="/var/log/mylog.json",
                              formatter=JsonObjectFormatter(
                                 template="MyLog: ${datetime} ${level|upper} ${message}"
                              )
                         )
                      ], 
                      filters=[ PackageFilter({"my.namespace":logging.INFO}) ]
    )

So what does the setup_handler do?
It attaches a handler to the specified logger to process the messages.
- min_level: The minimum log level needed for messages to be processed
- flush_level: Records are processed in batches, if a message with this level comes in the buffer is flushed immediately. (So setting it to DEBUG or NOTSET effectively disables the buffer)
- filters: Optional filters (viperlog.filters.IFilter protocol) to accept/reject messages based on the configuration. The PackageFilter in the example allows you to configure minimum log levels for namespaces without modifying the underlying logger instances. This can be useful if you would want different loglevels for different processors.
- processors: These instances of viperlog.processors.IProcessor take the messages, format and transport them to somewhere. The ConsoleProcessor will output to the console, the FileProcessor to a file etc.  

Most of the processors will accept a viperlog.formatters.IFormatter or a template string that will be used to format the log message 


You can call the setup_handler multiple times with different settings. In the above example the Console & File processors are combined, 
but you could setup separate handlers for them with different settings.


