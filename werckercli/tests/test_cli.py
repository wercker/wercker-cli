# import os
import mock

from werckercli.tests import (
    TestCase,
    VALID_GITHUB_SSH_URL,
    # VALID_BITBUCKET_SSH_URL,
)

from werckercli import cli
from werckercli.git import RemoteOption


class PrintIntroTtests(TestCase):

    def test_get_intro(self):

        result = cli.get_intro()

        self.assertTrue(result.find('wercker') != -1)


class HanldeCommandsTests(TestCase):

    @mock.patch('werckercli.authentication.get_access_token', mock.Mock())
    @mock.patch('werckercli.commands.create.create', mock.Mock())
    @mock.patch('werckercli.commands.login.login', mock.Mock())
    @mock.patch('werckercli.authentication.get_access_token', mock.Mock())
    @mock.patch(
        'werckercli.commands.clearsettings.clear_settings',
        mock.Mock()
    )
    @mock.patch(
        'werckercli.commands.project.project_list',
        mock.Mock()
    )
    def test_implemented_base_commands(self):
        my_cli = cli
        with mock.patch('werckercli.commands.target.add', mock.Mock()):
            with mock.patch(
                'werckercli.authentication.get_access_token',
                mock.Mock()
            ):

                # create
                my_cli.handle_commands(
                    {
                        'app': False,
                        'create': True,
                        'deploy': False,
                        'builds': False,
                        'logout': False,
                        'login': False,
                        'target': False,
                    }
                )

                #app create
                my_cli.handle_commands(
                    {
                        'app': True,
                        'create': True,
                        'builds': False,
                        'deploy': False,
                        'logout': False,
                        'login': False,
                        'target': False,
                    }
                )

                # logout
                my_cli.handle_commands(
                    {
                        'app': False,
                        'create': False,
                        'builds': False,
                        'deploy': False,
                        'logout': True,
                        'login': False,
                        'target': False,
                    }
                )

                my_cli.handle_commands(
                    {
                        'add': False,
                        'app': False,
                        'builds': False,
                        'create': False,
                        'deploy': False,
                        'logout': False,
                        'login': True,
                        'target': False,
                    }
                )

                # deploy add
                my_cli.handle_commands(
                    {
                        'add': True,
                        'app': False,
                        'builds': False,
                        'create': False,
                        'deploy': False,
                        'logout': False,
                        'login': False,
                        'target': True,
                    }
                )


class EnterUrlTests(TestCase):

    @mock.patch('werckercli.prompt.yn', mock.Mock(return_value=True))
    @mock.patch('werckercli.git.get_priority', mock.Mock(return_value=1))
    @mock.patch(
        '__builtin__.raw_input',
        mock.Mock(return_value=VALID_GITHUB_SSH_URL)
    )
    def test_valid_ssh(self):
        my_cli = reload(cli)
        result = my_cli.enter_url()

        self.assertEqual(result, VALID_GITHUB_SSH_URL)

    @mock.patch('clint.textui.puts', mock.Mock(return_value=False))
    @mock.patch('werckercli.prompt.yn', mock.Mock(return_value=True))
    @mock.patch('werckercli.git.get_priority', mock.Mock(return_value=0))
    @mock.patch(
        '__builtin__.raw_input',
        mock.Mock(return_value="INVALID_GITHUB_SSH_URL")
    )
    def test_force_unknown_location(self):
        my_cli = reload(cli)
        result = my_cli.enter_url(loop=False)

        self.assertEqual(result, "INVALID_GITHUB_SSH_URL")

    @mock.patch('clint.textui.puts', mock.Mock(return_value=False))
    @mock.patch('werckercli.prompt.yn', mock.Mock(return_value=False))
    @mock.patch('werckercli.git.get_priority', mock.Mock(return_value=0))
    @mock.patch(
        '__builtin__.raw_input',
        mock.Mock(return_value="INVALID_GITHUB_SSH_URL")
    )
    def test_invalid_location_no_loop(self):
        my_cli = cli
        result = my_cli.enter_url(loop=False)

        self.assertEqual(result, None)


class PickUrlOneOptionTests(TestCase):

    repo_name = "github-ssh"

    options = [
        RemoteOption(VALID_GITHUB_SSH_URL,  "origin", 2),
        # RemoteOption(VALID_URL+'2',  "secondary", 1),
        # RemoteOption('VALID_URL',  "other", 0)
    ]

    @mock.patch("__builtin__.raw_input", mock.Mock(return_value=""))
    @mock.patch("werckercli.cli.enter_url", mock.Mock(return_value=""))
    @mock.patch("clint.textui.puts", mock.Mock())
    def test_create_default(self):

        my_cli = reload(cli)
        result = my_cli.pick_url(self.options)
        self.assertEqual(
            result,
            "git@github.com:wercker/wercker-bruticus.git"
        )

    @mock.patch("__builtin__.raw_input", mock.Mock(return_value="1"))
    @mock.patch("werckercli.cli.enter_url", mock.Mock(return_value=""))
    @mock.patch("clint.textui.puts", mock.Mock())
    def test_create_1(self):

        my_cli = reload(cli)
        result = my_cli.pick_url(self.options)
        self.assertEqual(
            result,
            VALID_GITHUB_SSH_URL
        )

    @mock.patch("__builtin__.raw_input", mock.Mock(return_value="2"))
    @mock.patch("clint.textui.puts", mock.Mock())
    def test_create_2(self):

        my_cli = reload(cli)
        with mock.patch(
            "werckercli.cli.enter_url",
            mock.Mock(return_value="VALID_URL")
        ):

            result = my_cli.pick_url(self.options)
        self.assertEqual(
            result,
            "VALID_URL"
        )

    @mock.patch(
        "__builtin__.raw_input",
        mock.Mock(side_effect=["1=default", "2"])
    )
    @mock.patch("clint.textui.puts", mock.Mock())
    def test_faulty_input(self):

        my_cli = reload(cli)
        with mock.patch(
            "werckercli.cli.enter_url",
            mock.Mock(return_value="VALID_URL")
        ):

            result = my_cli.pick_url(self.options)
        self.assertEqual(
            result,
            "VALID_URL"
        )


class PickUrlThreeOptionTests(TestCase):

    repo_name = "github-ssh"

    options = [
        RemoteOption(VALID_GITHUB_SSH_URL,  "origin", 2),
        RemoteOption(VALID_GITHUB_SSH_URL+'2',  "secondary", 1),
        RemoteOption('VALID_URL',  "other", 0)
    ]

    @mock.patch("__builtin__.raw_input", mock.Mock(return_value="2"))
    @mock.patch("clint.textui.puts", mock.Mock())
    def test_create_2(self):

        my_cli = reload(cli)
        result = my_cli.pick_url(self.options)
        self.assertEqual(
            result,
            VALID_GITHUB_SSH_URL + '2'
        )


class PickUrlOneLowPrioOptionTests(TestCase):

    repo_name = "github-ssh"

    options = [
        # RemoteOption(VALID_URL,  "origin", 2),
        # RemoteOption(VALID_URL+'2',  "secondary", 1),
        RemoteOption('VALID_URL',  "other", 0)
    ]

    @mock.patch("__builtin__.raw_input", mock.Mock(return_value="1"))
    @mock.patch("clint.textui.puts", mock.Mock())
    def test_create_2(self):

        my_cli = reload(cli)
        result = my_cli.pick_url(self.options)
        self.assertEqual(
            result,
            "VALID_URL"
        )


class PickProjectName(TestCase):

    @mock.patch(
        "werckercli.prompt.get_value_with_default",
        mock.Mock(return_value=VALID_GITHUB_SSH_URL)
    )
    @mock.patch(
        "clint.textui.puts",
        mock.Mock(return_value=VALID_GITHUB_SSH_URL)
    )
    def test_get_bitbucket_name(self):
        reload(cli)
        name = cli.pick_project_name(VALID_GITHUB_SSH_URL)
        self.assertEqual(name, VALID_GITHUB_SSH_URL)
