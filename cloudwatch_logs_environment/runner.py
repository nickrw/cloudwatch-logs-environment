import argparse
import os

from .confgen import ConfigFile


def main():
    parser = argparse.ArgumentParser(description='cloudwatch-logs-env')
    parser.add_argument(
        '--config-path', default='/etc/cloudwatch/logs-agent.conf')
    parser.add_argument(
        '--additional-section-dir', required=False)
    parser.add_argument(
        '--state-path', default='/run/cloudwatch/logs-agent-state')
    parser.add_argument(
        '--config-only', action='store_true')
    parser.add_argument(
        '--dry-run', action='store_true')
    args = parser.parse_args()

    cf = ConfigFile(config_path=args.config_path, state_path=args.state_path)
    cf.autoconfigure()
    cf.write()

    if args.additional_section_dir:
        with open(args.config_path, 'a') as wf:
            for path in os.listdir(args.additional_section_dir):
                fq_path = os.path.join(args.additional_section_dir, path)
                if not os.path.isfile(fq_path):
                    continue
                with open(fq_path, 'r') as rf:
                    wf.write(rf.read())

    if args.config_only:
        with open(args.config_path, 'r') as fh:
            print(fh.read(), end='')
        return

    exec_args = ['aws', 'logs', 'push', '--config-file', args.config_path]
    if args.dry_run:
        exec_args.append('--dry-run')

    os.execvp('aws', exec_args)


if __name__ == '__main__':
    main()
