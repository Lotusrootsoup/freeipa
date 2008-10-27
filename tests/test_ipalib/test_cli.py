# Authors:
#   Jason Gerard DeRose <jderose@redhat.com>
#
# Copyright (C) 2008  Red Hat
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; version 2 only
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""
Test the `ipalib.cli` module.
"""

from tests.util import raises, getitem, no_set, no_del, read_only, ClassChecker
from ipalib import cli, plugable, frontend, backend


def test_to_cli():
    """
    Test the `ipalib.cli.to_cli` function.
    """
    f = cli.to_cli
    assert f('initialize') == 'initialize'
    assert f('user_add') == 'user-add'


def test_from_cli():
    """
    Test the `ipalib.cli.from_cli` function.
    """
    f = cli.from_cli
    assert f('initialize') == 'initialize'
    assert f('user-add') == 'user_add'


def get_cmd_name(i):
    return 'cmd_%d' % i


class DummyCommand(object):
    def __init__(self, name):
        self.__name = name

    def __get_name(self):
        return self.__name
    name = property(__get_name)


class DummyAPI(object):
    def __init__(self, cnt):
        self.__cmd = plugable.NameSpace(self.__cmd_iter(cnt))

    def __get_cmd(self):
        return self.__cmd
    Command = property(__get_cmd)

    def __cmd_iter(self, cnt):
        for i in xrange(cnt):
            yield DummyCommand(get_cmd_name(i))

    def finalize(self):
        pass

    def register(self, *args, **kw):
        pass


class test_CLI(ClassChecker):
    """
    Test the `ipalib.cli.CLI` class.
    """
    _cls = cli.CLI

    def new(self, argv):
        api = plugable.API(
            frontend.Command,
            frontend.Object,
            frontend.Method,
            frontend.Property,
            frontend.Application,
            backend.Backend,
        )
        o = self.cls(api, argv)
        assert o.api is api
        return o

    def test_init(self):
        """
        Test the `ipalib.cli.CLI.__init__` method.
        """
        argv = ['-v', 'user-add', '--first=Jonh', '--last=Doe']
        o = self.new(argv)
        assert type(o.api) is plugable.API
        assert o.argv == tuple(argv)

    def test_parse_globals(self):
        """
        Test the `ipalib.cli.CLI.parse_globals` method.
        """
        # Test with empty argv
        o = self.new([])
        assert not hasattr(o, 'options')
        assert not hasattr(o, 'cmd_argv')
        assert o.isdone('parse_globals') is False
        o.parse_globals()
        assert o.isdone('parse_globals') is True
        assert o.options.interactive is True
        assert o.options.verbose is False
        assert o.options.config_file is None
        assert o.options.environment is None
        assert o.cmd_argv == tuple()
        e = raises(StandardError, o.parse_globals)
        assert str(e) == 'CLI.parse_globals() already called'

        # Test with a populated argv
        argv = ('-a', '-n', '-v', '-c', '/my/config.conf', '-e', 'my_key=my_val')
        cmd_argv = ('user-add', '--first', 'John', '--last', 'Doe')
        o = self.new(argv + cmd_argv)
        assert not hasattr(o, 'options')
        assert not hasattr(o, 'cmd_argv')
        assert o.isdone('parse_globals') is False
        o.parse_globals()
        assert o.isdone('parse_globals') is True
        assert o.options.prompt_all is True
        assert o.options.interactive is False
        assert o.options.verbose is True
        assert o.options.config_file == '/my/config.conf'
        assert o.options.environment == 'my_key=my_val'
        assert o.cmd_argv == cmd_argv
        e = raises(StandardError, o.parse_globals)
        assert str(e) == 'CLI.parse_globals() already called'
