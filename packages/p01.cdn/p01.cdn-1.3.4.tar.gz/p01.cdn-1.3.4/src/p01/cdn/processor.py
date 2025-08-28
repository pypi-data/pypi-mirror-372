##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Templated Resource Processor

$Id$
"""
__docformat__='restructuredtext'
import re
import zope.interface
import zope.component
from p01.cdn import interfaces

# <COMMAND-BEGIN> <ZRT-COMMAND>: <COMMAND-ARGUMENTS> <COMMAND-END>
NAME = r'[a-zA-Z0-9_-]*'
COMMAND_REGEX = r'%%s(%s):\s*(.*?)\s*%%s' %NAME

TEXTBLOCK=0
COMMAND=1
EXTRCOMMAND=2


@zope.interface.implementer(interfaces.IZRTProcessor)
class ZRTProcessor(object):
    """A ZRT Processor"""

    commandStartRegex = r'/\*\s*zrt-'
    commandEndRegex = r'\*/'

    def __init__(self, source, commands=None):
        # remember format
        self._source_was_bytes = isinstance(source, (bytes, bytearray))
        # normalize
        if self._source_was_bytes:
            try:
                source = source.decode('utf-8')
            except UnicodeDecodeError:
                # fallback, any other 8-bit encoding
                source = source.decode('latin-1')
        self.source = source
        if not commands:
            commands = {}
        self.commands = commands
        self._bytecode = None

    def compile(self):
        """See interfaces.IZRTProcessor"""
        bytecode = []
        pos = 0
        # Regular Expression to find commands.
        regex = re.compile(COMMAND_REGEX %(self.commandStartRegex,
                                           self.commandEndRegex))
        nextlinelen = 1
        if '\r\n' in self.source:
            # work around windows: it has a 2 char next line sequence
            nextlinelen = 2

        # Find all commands
        for match in regex.finditer(self.source):
            command, args = match.groups()

            # Add the previous text block and update position
            bytecode.append((TEXTBLOCK, self.source[pos:match.start()]))
            pos = match.end() + nextlinelen

            # Make sure the command exists
            if command not in self.commands:
                cmd = zope.component.queryUtility(
                    interfaces.IZRTCommandFactory, command)

                if cmd is None:
                    raise interfaces.UnknownZRTCommand(command)

                # Add the command
                bytecode.append((EXTRCOMMAND,
                                 (cmd, args, match.start(), match.end())))
            else:
                # Add the command
                bytecode.append(
                    (COMMAND, (command, args, match.start(), match.end())))

        # Add the final textblock
        bytecode.append((TEXTBLOCK, self.source[pos:]))

        self._bytecode = bytecode

    def process(self, context, request):
        """See interfaces.IZRTProcessor"""
        if self._bytecode is None:
            self.compile()

        # List active commands
        active = []
        result = []
        for type, value in self._bytecode:
            # If the type is a command, simply add it to the list of commands
            if type is COMMAND:
                cmd, args, start, end = value
                active.append(
                    self.commands[cmd](args, start, end))
            # If the type is a external command
            elif type is EXTRCOMMAND:
                cmd, args, start, end = value
                active.append(cmd(args, start, end))
            # If we have a textblock, then work on it.
            elif type is TEXTBLOCK:
                # Process any command
                for cmd in active:
                    value = cmd.process(value, context, request)
                    # If the command is no longer available, remove it
                    if not cmd.isAvailable:
                        active.remove(cmd)
                # This block is fully processed now.
                result.append(value)
            else:
                raise ValueError(type)

        out = ''.join(result)
        # encde in bytes if it was bytes
        if self._source_was_bytes:
            try:
                return out.encode('utf-8')
            except UnicodeEncodeError:
                return out.encode('latin-1', errors='replace')
        return out
