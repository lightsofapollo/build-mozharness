#!/usr/bin/env python
"""Logging, the way I remember it from scripts gone by.

TODO:
- network logging support.
- ability to change log settings mid-stream
- per-module log settings
- are we really forced to use global logging.* settings???
  - i hope i'm mistaken here
  - would love to do instance-based settings so we can have multiple
    objects that can each have their own logger
"""

from optparse import OptionParser
import logging
import os
import sys

# Define our own FATAL
FATAL = logging.CRITICAL + 10
logging.addLevelName(FATAL, 'FATAL')



# BaseLogger {{{1
class BaseLogger(object):
    """Create a base logging class.
    TODO: be able to set defaults from config/parseArgs if self
    also inherits Config.
    """
    LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL,
              'fatal': logging.FATAL
             }

    def __init__(self, defaultLogLevel='info',
                 defaultLogFormat='%(message)s',
                 defaultLogDateFormat='%H:%M:%S',
                 logToConsole=True,
                 haltOnFailure=True,
                ):
        self.haltOnFailure = haltOnFailure,
        self.defaultLogFormat = defaultLogFormat
        self.defaultLogDateFormat = defaultLogDateFormat
        self.logToConsole = logToConsole
        self.defaultLogLevel = defaultLogLevel
        
        self.allHandlers = []

    def getLoggerLevel(self, level=None):
        if not level:
            level = self.defaultLogLevel
        return self.LEVELS.get(level, logging.NOTSET)

    def getLogFormatter(self, logFormat=None, dateFormat=None):
        if not logFormat:
            logFormat = self.defaultLogFormat
        if not dateFormat:
            dateFormat = self.defaultLogDateFormat
        return logging.Formatter(logFormat, dateFormat)

    def newLogger(self, loggerName):
        """Create a new logger.
        By default there are no handlers.
        """
        self.logger = logging.getLogger(loggerName)
        self.logger.setLevel(self.getLoggerLevel())
        self._clearHandlers()
        if self.logToConsole:
            self.addConsoleHandler()

    def _clearHandlers(self):
        """To prevent dups -- logging will preserve Handlers across
        objects :(
        """
        attrs = dir(self)
        if 'allHandlers' in attrs and 'logger' in attrs:
            for handler in self.allHandlers:
                self.logger.removeHandler(handler)
            self.allHandlers = []

    def __del__(self):
        self._clearHandlers()

    def addConsoleHandler(self, logLevel=None, logFormat=None,
                          dateFormat=None):
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(self.getLoggerLevel(logLevel))
        consoleHandler.setFormatter(self.getLogFormatter(logFormat=logFormat,
                                                         dateFormat=dateFormat))
        self.logger.addHandler(consoleHandler)
        self.allHandlers.append(consoleHandler)

    def addFileHandler(self, logName, logLevel=None, logFormat=None,
                       dateFormat=None):
        fileHandler = logging.FileHandler(logName)
        fileHandler.setLevel(self.getLoggerLevel(logLevel))
        fileHandler.setFormatter(self.getLogFormatter(logFormat=logFormat,
                                                      dateFormat=dateFormat))
        self.logger.addHandler(fileHandler)
        self.allHandlers.append(fileHandler)

    def log(self, message, level='info', exitCode=-1):
        """Generic log method.
        There should be more options here -- do or don't split by line,
        use os.linesep instead of assuming \n, be able to pass in log level
        by name or number.
        """
        for line in message.split('\n'):
            self.logger.log(self.getLoggerLevel(level), line)
        if level == 'fatal' and self.haltOnFailure:
            self.logger.log(FATAL, 'Exiting %d' % exitCode)
            sys.exit(exitCode)



# SimpleFileLogger {{{1
class SimpleFileLogger(BaseLogger):
    """Create one logFile.  Possibly also output to
    the terminal and a raw log (no prepending of level or date)
    """
    def __init__(self, logDir='.', logName='test.log',
                 defaultLogFormat='%(asctime)s - %(levelname)s - %(message)s',
                 options=None, longOptions=None,
                 loggerName='Simple', **kwargs):
        self.loggerName = loggerName
        self.logName = logName
        self.logDir = logDir
        BaseLogger.__init__(self, defaultLogFormat=defaultLogFormat,
                            **kwargs)
        self.newLogger(self.loggerName)

    def newLogger(self, loggerName):
        BaseLogger.newLogger(self, loggerName)
        self.logPath = os.path.join(os.getcwd(), self.logName)
        self.addFileHandler(self.logPath)




# MultiFileLogger {{{1
class MultiFileLogger(BaseLogger):
    """Create a log per log level in logDir.  Possibly also output to
    the terminal and a raw log (no prepending of level or date)
    """
    def __init__(self, baseLogName='test',
                 defaultLogFormat='%(asctime)s - %(levelname)s - %(message)s',
                 loggerName='', logDir='logs', logToRaw=True, **kwargs):
        self.baseLogName = baseLogName
        self.logDir = logDir
        self.loggerName = loggerName
        self.logToRaw = logToRaw
        self.logFiles = {}
        BaseLogger.__init__(self, defaultLogFormat=defaultLogFormat,
                            **kwargs)

        self.createLogDir()
        self.newLogger(self.loggerName)

    def createLogDir(self):
        if os.path.exists(self.logDir):
            if not os.path.isdir(self.logDir):
                os.remove(self.logDir)
        if not os.path.exists(self.logDir):
            os.makedirs(self.logDir)
        self.absLogDir = os.path.abspath(self.logDir)

    def newLogger(self, loggerName):
        BaseLogger.newLogger(self, loggerName)
        if self.logToRaw:
            self.logFiles['raw'] = '%s_raw.log' % self.baseLogName
            self.addFileHandler(os.path.join(self.absLogDir,
                                             self.logFiles['raw']),
                                logFormat='%(message)s')
        minLoggerLevel = self.getLoggerLevel(self.defaultLogLevel)
        for level in self.LEVELS.keys():
            if self.getLoggerLevel(level) >= minLoggerLevel:
                self.logFiles[level] = '%s_%s.log' % (self.baseLogName,
                                                      level)
                self.addFileHandler(os.path.join(self.absLogDir,
                                                 self.logFiles[level]),
                                    logLevel=level)



# __main__ {{{1

if __name__ == '__main__':
    """Quick 'n' dirty unit tests.
    Ideally, this would be parsed automatically, too, and wouldn't leave
    cruft behind.
    """
    def testLogger(obj):
        obj.log('YOU SHOULD NOT SEE THIS LINE', level='debug')
        for level in ('info', 'warning', 'error', 'critical'):
            obj.log('test %s' % level, level=level)
        try:
            obj.log('test fatal -- you should see an exit line after this.',
                    level='fatal')
        except:
            print "Yay, that's good."
        else:
            print "OH NO!"

    logDir = 'test_logs'
    obj = MultiFileLogger(defaultLogLevel='info', logDir=logDir,
                          logToRaw=True)
    testLogger(obj)
    obj.haltOnFailure=False
    obj.log('test fatal -- you should *not* see an exit line after this.',
            level='fatal')
    obj = SimpleFileLogger()
    testLogger(obj)
    print "=========="
    print "You should be able to examine test.log and %s." % logDir
