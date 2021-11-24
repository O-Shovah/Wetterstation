import logging

class MyModule(object):
#"""
#Sample module to demonstrate setting of loglevel on init
#"""
    def __init__(self, logLevel):
        #logLevel, a string, should be one of the levels of the logging modules. Example: DEBUG, INFO, WARNING etc.
        #Translate the logLevel input string to one of the accepted values of the logging module. Change it to upper to allow calling module to use lowercase 
        #If it doesn't translate default to something like DEBUG which is 10
        numeric_level = getattr(logging, logLevel.upper(), 10)

        logging.basicConfig(filename='example.log', level=numeric_level)


    def testLogger(self):
        #logging object that you defined the level in init is used here for some sample logging
        logging.debug('see this at debug level')
        logging.info('see this at info and debug')
        logging.warning('see this at warn, info and debug')


if __name__ == "__main__":
    MM= MyModule('info')
    MM.testLogger()