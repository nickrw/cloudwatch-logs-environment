# CloudWatch Logs - environment based configuration

This utility generates an agent configuration file based on environment
variables, and then runs the agent on this configuration.

This is ideal for docker environments where generating a configuration file
on the host in order to share it to your log agent container is painful.


## How it works

It looks for environment variables named `*_LOG_GROUP_NAME`, and writes a
configuration section named after the wildcard portion `*`. Any other
variable named with the same prefix will be written as a key/value pair in
that section.

E.g. `FOO_LOG_GROUP_NAME=bar FOO_FILE=/path/to/file.log` becomes

```
[foo]
log_group_name = bar
file = /path/to/file.log
log_stream_name = 20161117_1824_{hostname}
time_zone = UTC
initial_position = start_of_file
```

Note that some defaults will be filled in if you don't provide them. In
particular the stream name will try to be as unique as possible to avoid
collisions. This is designed to be used from within a docker container, so
hostname (container id) is used instead of `{instance_id}`.

For a section to be written to the config file you must provide both a
`*_LOG_GROUP_NAME` and `*_FILE` variable.

Variables beginning `CWLOGS_*` will be transformed into options in the
`[general]` section, with the exception of `CWLOGS_STATE_FILE`.


## Configuration examples

An example agent configuration file looks something like this

```
[general]
state_file = /run/cloudwatch/logs-agent-state
use_gzip_http_content_encoding = true

[access_log]
log_group_name = access_log
log_stream_name = {hostname}
datetime_format = %Y-%m-%dT%H:%M:%S
time_zone = UTC
file = /var/log/httpd/access.log

[error_log]
log_group_name = error_log
log_stream_name = {hostname}
file = /var/log/httpd/error.log
buffer_duration = 1000
```

You can generate a file that looks like the above by setting the following
environment variables:

```
CWLOGS_USE_GZIP_HTTP_CONTENT_ENCODING=true \
ACCESS_LOG_LOG_GROUP_NAME=access_log \
ACCESS_LOG_LOG_STREAM_NAME="{hostname}" \
ACCESS_LOG_DATETIME_FORMAT="%Y-%m-%dT%H:%M:%S" \
ACCESS_LOG_TIME_ZONE=UTC \
ACCESS_LOG_FILE=/var/log/httpd/access.log \
ERROR_LOG_LOG_GROUP_NAME=error_log \
ERROR_LOG_LOG_STREAM_NAME="{hostname}" \
ERROR_LOG_FILE=/var/log/httpd/error.log \
ERROR_LOG_BUFFER_DURATION=1000 \
cwlogs_env_runner --config-only
```

Full agent config file options can be found at
http://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AgentReference.html


## Running

Simply set the environment variables for the sections you require and run
`cwlogs_env_runner`.

`cwlogs_env_runner` takes a few options:

* `--config-path=PATH` the path to write the config file to, and to point the agent
  at

* `--state-path=PATH` the state file to configure the agent to use. This defaults
  to `/run/cloudwatch/logs-agent-state`

* `--config-only` if present will write the config file (and print it), but
  not execute the agent.

* `--dry-run` if present will execute the agent in dry-run mode


## Running in docker

Mount your log files into the container, or share logs between containers
using volumes.

```
docker run \
  -e AWS_DEFAULT_REGION=eu-west-1 \
  -e ACCESS_LOG_LOG_GROUP_NAME=access_log \
  -e ACCESS_LOG_DATETIME_FORMAT="%Y-%m-%dT%H:%M:%S" \
  -e ACCESS_LOG_TIME_ZONE=UTC \
  -e ACCESS_LOG_FILE=/var/log/httpd/access.log \
  -v /var/log/httpd/access.log:/var/log/httpd/access.log \
  nickrw/cloudwatch-logs-environment:latest
```

If you are not running this on an ec2 instance with role-based permissions you
will also need to provide access keys via the environment: `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`
