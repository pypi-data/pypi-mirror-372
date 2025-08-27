# pylint:disable=line-too-long,too-many-arguments,too-many-positional-arguments
"""
LOCI CLI
"""

import argparse
import json
import sys
import os

from loci_api import api_helper

def parse_args():
    program_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser(prog=program_name, description="LOCI CLI")
    subparsers = parser.add_subparsers(dest="command", required=False)

    projects_parser = subparsers.add_parser("list-projects", help="List all projects")
    projects_parser.add_argument("-o", "--output", help="Output file path. Default: stdout", type=str, default=None)

    list_versions_parser = subparsers.add_parser("list-versions", help="List all versions of a project")
    list_versions_parser.add_argument("project-name", help="Project name", type=str)
    list_versions_parser.add_argument("-o", "--output", help="Output file path. Default: stdout", type=str, default=None)

    last_version_parser = subparsers.add_parser("last-version", help="Get last version of a project")
    last_version_parser.add_argument("project-name", help="Project name", type=str)
    last_version_parser.add_argument("-o", "--output", help="Output file path. Default: stdout", type=str, default=None)

    upload_parser = subparsers.add_parser("upload", help="Upload a new version")
    upload_parser.add_argument("path-to-binary", help="Binary file", type=str)
    upload_parser.add_argument("project-name", help="Project name", type=str)
    upload_parser.add_argument("new-version-name", help="Version name", type=str)
    upload_parser.add_argument("--compare-version-name", help="Version to compare", type=str)
    upload_parser.add_argument("--wait", help="wait for processing to finish", type=str, default='True')
    upload_parser.add_argument("--event-id", help="id of object event initiating the action", type=str, default='')

    upload_last_parser = subparsers.add_parser("upload-last", help="Upload a new version using latest")
    upload_last_parser.add_argument("path-to-binary", help="Binary file", type=str)
    upload_last_parser.add_argument("project-name", help="Project name", type=str)
    upload_last_parser.add_argument("new-version-name", help="Version name", type=str)
    upload_last_parser.add_argument("--wait", help="wait for processing to finish", type=str, default='True')
    upload_last_parser.add_argument("--event-id", help="id of object event initiating the action", type=str, default='')

    status_parser = subparsers.add_parser("status", help="Check status of a version")
    status_parser.add_argument("project-name", help="Project name", type=str)
    status_parser.add_argument("version-name", help="Version name", type=str)
    status_parser.add_argument("-o", "--output", help="Output file path. Default: stdout", type=str, default=None)

    func_insights_parser = subparsers.add_parser("func-insights", help="Get function insights")
    func_insights_parser.add_argument("project-name", help="Project name", type=str)
    func_insights_parser.add_argument("version-name", help="Version name", type=str)
    func_insights_parser.add_argument("--version-name-base", help="Base version name", type=str, default=None)
    func_insights_parser.add_argument("--perc-resp-limit", help="Response time limit (percentage)", type=float, default=None)
    func_insights_parser.add_argument("--perc-thro-limit", help="Throughput limit (percentage)", type=float, default=None)
    func_insights_parser.add_argument("--perc-bott-limit", help="Bottleneck limit (percentage)", type=float, default=None)
    func_insights_parser.add_argument("--pairs", nargs='*', default=[],
                                      help="Pairs of function_name and binary_name, e.g. --pairs func1 bin1 func2 bin2")
    func_insights_parser.add_argument("-o", "--output", help="Output file path. Default: stdout", type=str, default=None)

    flame_graph_parser = subparsers.add_parser("flame-graph", help="Generate flame graph for a function")
    flame_graph_parser.add_argument("project-name", help="Project name", type=str)
    flame_graph_parser.add_argument("version-name", help="Version name", type=str)
    flame_graph_parser.add_argument("--function-name", help="Function long name", type=str)
    flame_graph_parser.add_argument("--binary-name", help="Binary/container name", type=str)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    return args

def output_success_result(res, output = None) -> int:
    data = json.dumps(res, indent=2)
    if output:
        with open(output, 'w') as f:
            f.write(data)
    else:
        print(data)
    return 0

def cmd_list_projects(output) -> int:
    projects = api_helper.get_projects()
    if projects is None:
        return 1
    res = [project['name'] for project in projects]
    return output_success_result(res, output)

def cmd_list_versions(project_name, output) -> int:
    project_id, _ = api_helper.get_project_id(project_name)
    if project_id is None:
        return 1
    versions = api_helper.get_versions(project_id)
    if versions is None:
        return 1
    res = []
    for version in versions:
        res.append({
            "name": version['properties']['version_name'],
            "started_at": version['properties']['start_dt']
        })
    return output_success_result(res, output)

def cmd_last_version(project_name, output) -> int:
    project_id, _ = api_helper.get_project_id(project_name)
    if project_id is None:
        return 1
    _, version_name = api_helper.get_last_version_id(project_id)
    if version_name is None:
        return 1
    return output_success_result([version_name], output)

def cmd_upload(file_path, project_name, version_name, cmp_ver_name, wait, event_id) -> int:
    compare_version_id = ''
    if cmp_ver_name:
        project_id, _ = api_helper.get_project_id(project_name)
        versions = api_helper.get_versions(project_id)
        for version in versions:
            if cmp_ver_name == version['properties']['version_name']:
                compare_version_id = version['properties']['version_id']
    return api_helper.full_upload(file_path, version_name, project_name, use_latest=False, compare_version_id=compare_version_id, wait=wait, event_id=event_id)

def cmd_upload_last(file_path, project_name, version_name, wait, event_id) -> int:
    return api_helper.full_upload(file_path, version_name, project_name, use_latest=True, compare_version_id='', wait=wait, event_id=event_id)

def cmd_function_insights(project_name, version_name, version_name_base, perc_resp_limit, perc_thro_limit, perc_bott_limit, pairs, output) -> int:
    if pairs:
        if len(pairs) % 2 != 0:
            print(f'uneven number of pairs: {len(pairs)}')
            return 1
        pairs = [{"function_name": pairs[i], "binary_name": pairs[i + 1]} for i in range(0, len(pairs), 2)]

    project_id, _ = api_helper.get_project_id(project_name)
    if not project_id:
        return 1

    versions = api_helper.get_versions(project_id)
    if not versions:
        return 1

    version_id = None
    version_id_base = None

    for version in versions:
        if version_name == version['properties']['version_name']:
            version_id = version['properties']['version_id']
        if version_name_base == version['properties']['version_name']:
            version_id_base = version['properties']['version_id']

    if not version_id:
        print('Version not found')
        return 1

    insights = api_helper.get_function_insights(version_id, version_id_base, perc_resp_limit, perc_thro_limit, perc_bott_limit, pairs)
    if insights is None:
        return 1

    def _to_insight(insight, has_base_version):
        res = {
            'total_count': insight['total_count'],
            'binary_name': insight['binary_name'],
            'function_long_name': insight['function_long_name'],
            'function_name': insight['function_name'],
            'source_location': insight['src_location'],
            'mean_bottleneck': insight['mean_bottleneck'],
            'std_bottleneck': insight['std_bottleneck'],
            'mean_throughput': insight['mean_throughput'],
            'std_throughput': insight['std_throughput'],
            'mean_response': insight['mean_resp'],
            'std_response': insight['std_resp'],
        }
        if has_base_version:
            res.update({
                'mean_bottleneck_base': insight['mean_bottleneck_base'],
                'std_bottleneck_base': insight['std_bottleneck_base'],
                'mean_throughput_base': insight['mean_throughput_base'],
                'std_throughput_base': insight['std_throughput_base'],
                'mean_response_base': insight['mean_resp_base'],
                'std_response_base': insight['std_resp_base'],
                'perc_throughput': insight['perc_thro'],
                'perc_response': insight['perc_resp'],
                'perc_bottleneck': insight['perc_bott'],
            })
        return res
    
    return output_success_result([_to_insight(i, version_id_base is not None) for i in insights['message']], output)


def cmd_flame_graph(project_name, version_name, function_name, binary_name) -> int:
    project_id, _ = api_helper.get_project_id(project_name)
    if not project_id:
        return 1

    versions = api_helper.get_versions(project_id)
    if not versions:
        return 1

    version_id = None

    for version in versions:
        if version_name == version['properties']['version_name']:
            version_id = version['properties']['version_id']

    if not version_id:
        print('Version not found')
        return 1

    res = api_helper.get_flame_graph(project_id, version_id, binary_name, function_name)
    if res is None:
        return 1
    
    return output_success_result(res["message"])


def cmd_status(project_name, version_name, output) -> int:
    project_id, _ = api_helper.get_project_id(project_name)
    if project_id is None:
        return 1

    versions = api_helper.get_versions(project_id)
    if versions is None:
        return 1

    version_id = None

    for version in versions:
        if version_name == version['properties']['version_name']:
            version_id = version['properties']['version_id']
            break

    if version_id is None:
        print("Version not found")
        return 1

    result = api_helper.get_project_status(project_id, version_id)
    if not result:
        return 1

    statuses = result['progress']['statuses']
    formatted_result = {
        "status": result['progress']['status'],
        "total": len(result['progress']['containers']),
        "counts": {
            "passed": sum(1 for s in statuses if s == 0),
            "failed": sum(1 for s in statuses if s > 0),
            "pending": sum(1 for s in statuses if s == -1),
        },
        "updated_at": result['progress']['end_dt'],
        "analysis": []
    }
    for idx, container in enumerate(result['progress']['containers']):
        formatted_result["analysis"].append({
            "binary": container,
            "step": result['progress']['actions'][idx],
            "status": result['progress']['statuses'][idx],
            "updated_at": result['progress']['action_timestamps'][idx]
        })
    return output_success_result(formatted_result, output)


def main():
    args = parse_args()

    if args.command == "list-projects":
        sys.exit(cmd_list_projects(output=args.output))

    if args.command == "list-versions":
        sys.exit(cmd_list_versions(project_name=getattr(args, 'project-name'), output=args.output))

    if args.command == "last-version":
        sys.exit(cmd_last_version(project_name=getattr(args, 'project-name'), output=args.output))

    if args.command == "status":
        sys.exit(cmd_status(project_name=getattr(args, 'project-name'), version_name=getattr(args, 'version-name'), output=args.output))

    if args.command == "upload":
        sys.exit(cmd_upload(file_path=getattr(args, 'path-to-binary'),
                            project_name=getattr(args, 'project-name'),
                            version_name=getattr(args, 'new-version-name'),
                            cmp_ver_name=getattr(args, 'compare_version_name', None),
                            wait=getattr(args, 'wait', None),
                            event_id=getattr(args, 'event_id', None)))

    if args.command == "upload-last":
        sys.exit(cmd_upload_last(file_path=getattr(args, 'path-to-binary'),
                                 project_name=getattr(args, 'project-name'),
                                 version_name=getattr(args, 'new-version-name'),
                                 wait=getattr(args, 'wait', None),
                                 event_id=getattr(args, 'event_id', None)))

    if args.command == "func-insights":
        sys.exit(cmd_function_insights(project_name=getattr(args, 'project-name'),
                                       version_name=getattr(args, 'version-name'),
                                       version_name_base=getattr(args, 'version_name_base', None),
                                       perc_resp_limit=getattr(args, 'perc_resp_limit', None),
                                       perc_thro_limit=getattr(args, 'perc_thro_limit', None),
                                       perc_bott_limit=getattr(args, 'perc_bott_limit', None),
                                       pairs=getattr(args, 'pairs', None),
                                       output=args.output))
        
    if args.command == "flame-graph":
        sys.exit(cmd_flame_graph(project_name=getattr(args, 'project-name'),
                                 version_name=getattr(args, 'version-name'),
                                 function_name=getattr(args, 'function_name'),
                                 binary_name=getattr(args, 'binary_name')))

if __name__ == "__main__":
    main()
