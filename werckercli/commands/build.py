from werckercli.decorators import login_required
from werckercli.client import Client
from werckercli.prompt import get_value_with_default
from werckercli.printer import (
    store_highest_length,
    print_hr,
    print_line,
    format_date,
)

# from werckercli.commands.target import
from werckercli.cli import term, puts

from werckercli.config import (
    get_value,
    VALUE_PROJECT_ID
)

from werckercli.commands.target import (
    # get_targets,
    # print_targets,
    pick_target
)


@login_required
def build_list(valid_token=None, limit=5):

    if not valid_token:
        raise ValueError("A valid token is required!")

    projectId = get_value(VALUE_PROJECT_ID)

    if not projectId:
        puts(
            term.red("Error: ") +
            "No project found. Please create or link a project first"
        )

        return

    builds = get_builds(valid_token, projectId)
    print_builds(builds, limit=limit)


@login_required
def build_deploy(valid_token=None):

    if not valid_token:
        raise ValueError("A valid token is required!")

    projectId = get_value(VALUE_PROJECT_ID)

    if not projectId:
        puts(
            term.red("Error: ") +
            "No project found. Please create or link a project first"
        )

    builds = get_builds(valid_token, projectId)

    if type(builds) is not list or len(builds) == 0:
        puts(term.yellow("warning: ") + "No builds found.")
        return

    passed_builds = [build for build in builds if build['result'] == "passed"]
    if len(passed_builds) == 0:
        puts("No passed deploys found.")
    print_builds(passed_builds, print_index=True)

    deploy_index = -1
    target_index = -1

    while(True):
        result = get_value_with_default("Select which build to deploy", '1')

        valid_values = [str(i + 1) for i in range(len(passed_builds))]
        # valid_values = range(1, len(passed_builds) + 1)

        # print valid_values, result
        if result in valid_values:
            deploy_index = valid_values.index(result)
            break
        else:
            puts(term.red("warning: ") + " invalid build selected.")

    target_index = pick_target(valid_token, projectId)

    c = Client()

    code, result = c.do_deploy(
        valid_token,
        passed_builds[deploy_index]['id'],
        target_index
    )

    if "success" in result and result['success'] is True:
        puts(term.green("Build scheduled for deploy"))
    else:
        puts(term.red("Error: ") + "Unable to schedule deploy")


def get_builds(valid_token, projectId):
    c = Client()

    puts("Retreiving builds from wercker...")
    status, result = c.get_builds(valid_token, projectId)

    return result


def print_builds(builds, print_index=False, limit=5):

    result = builds

    header = [
        'result',
        'progress',
        'branch',
        'hash',
        'created',
        'message',
    ]

    props = [
        'result',
        'progress',
        'branch',
        # 'deployResult',
        # 'deployBy',
        # 'deployFinishedOn',
        # 'branch',
        'commit',
        'creationDate',
        # 'deployStatus',
        'commitMessage',
    ]

    if print_index:
        header = [''] + header
        props = ['index'] + props

    max_lengths = []

    for i in range(len(header)):
        max_lengths.append(0)

    store_highest_length(max_lengths, header)

    if type(result) is list:
        index = 0
        result = result[:limit]
        if type(result) is list:
            puts("Found %d result(s)...\n" % len(result))

        for row in result:
            if "startedOn" in row:
                row['creationDate'] = format_date(row['creationDate'])

            if "progress" in row:
                row['progress'] = "{progress:.1f}%".format(
                    progress=row['progress'])

            if "commit" in row:
                row["commit"] = row['commit'][:8]

            if print_index:
                row['index'] = index + 1

            store_highest_length(max_lengths, row, props)

            index += 1

        print_hr(max_lengths, first=True)
        print_line(max_lengths, header)
        print_hr(max_lengths)

        for row in result:
            print_line(max_lengths, row, props)
        print_hr(max_lengths)


@login_required
def monitor_builds(valid_token=None):

    if not valid_token:
        raise ValueError("A valid token is required!")

    from werckercli.commands.project import project_build

    buildId = project_build(valid_token=valid_token)

    if buildId:
        puts(buildId)

    cl = Client()

    while True:

    # cl = Client()
