# coding: utf-8

import six


class TestgresException(Exception):
    pass


class PortForException(TestgresException):
    pass


@six.python_2_unicode_compatible
class ExecUtilException(TestgresException):
    def __init__(self, message=None, command=None, exit_code=0, out=None, error=None):
        super(ExecUtilException, self).__init__(message)

        self.message = message
        self.command = command
        self.exit_code = exit_code
        self.out = out
        self.error = error

    def __str__(self):
        msg = []

        if self.message:
            msg.append(self.message)

        if self.command:
            command_s = ' '.join(self.command) if isinstance(self.command, list) else self.command,
            msg.append(u'Command: {}'.format(command_s))

        if self.exit_code:
            msg.append(u'Exit code: {}'.format(self.exit_code))

        if self.error:
            msg.append(u'---- Error:\n{}'.format(self.error))

        if self.out:
            msg.append(u'---- Out:\n{}'.format(self.out))

        return self.convert_and_join(msg)

    @staticmethod
    def convert_and_join(msg_list):
        # Convert each byte element in the list to str
        str_list = [six.text_type(item, 'utf-8') if isinstance(item, bytes) else six.text_type(item) for item in
                    msg_list]

        # Join the list into a single string with the specified delimiter
        return six.text_type('\n').join(str_list)


@six.python_2_unicode_compatible
class QueryException(TestgresException):
    def __init__(self, message=None, query=None):
        super(QueryException, self).__init__(message)

        self.message = message
        self.query = query

    def __str__(self):
        msg = []

        if self.message:
            msg.append(self.message)

        if self.query:
            msg.append(u'Query: {}'.format(self.query))

        return six.text_type('\n').join(msg)


class TimeoutException(QueryException):
    pass


class CatchUpException(QueryException):
    pass


@six.python_2_unicode_compatible
class StartNodeException(TestgresException):
    def __init__(self, message=None, files=None):
        super(StartNodeException, self).__init__(message)

        self.message = message
        self.files = files

    def __str__(self):
        msg = []

        if self.message:
            msg.append(self.message)

        for f, lines in self.files or []:
            msg.append(u'{}\n----\n{}\n'.format(f, lines))

        return six.text_type('\n').join(msg)


class InitNodeException(TestgresException):
    pass


class BackupException(TestgresException):
    pass


class InvalidOperationException(TestgresException):
    pass
