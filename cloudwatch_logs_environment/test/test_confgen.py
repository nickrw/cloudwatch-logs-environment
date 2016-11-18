from configparser import RawConfigParser
from copy import copy
from uuid import uuid4

import pytest

from ..confgen import (
    ConfigFile,
    SECTION_DEFAULTS,
    section_name_is_valid,
    extract_section_options_from_env,
    extract_sections_from_env,
)

sections = ('access_log', 'other_log', '/var/log/logfile')


def options_for_name(name):
    return {
        'log_group_name': 'foo',
        'file': '{}.log'.format(name),
        'time_zone': 'local',
        'xyz': "ASD4 * ' da\\$"
    }


def options_for_name_defaults(name):
    options = copy(SECTION_DEFAULTS)
    options.update(options_for_name(name))
    return options


@pytest.fixture
def setup(monkeypatch):
    for section in sections:
        for option, value in options_for_name(section).items():
            env_var_name = '{}_{}'.format(section.upper(), option.upper())
            monkeypatch.setenv(env_var_name, value)


@pytest.mark.parametrize("section_name", sections)
def test_section_options_from_env(setup, section_name):
    options = extract_section_options_from_env(section_name.upper())
    assert options == options_for_name_defaults(section_name)


def test_sections_from_env(setup):
    options = dict(extract_sections_from_env())
    assert options == {k: options_for_name_defaults(k) for k in options}


def test_section_validity(monkeypatch):
    monkeypatch.setenv('INVALID_LOG_GROUP_NAME', 'group')
    assert section_name_is_valid('INVALID') is False
    monkeypatch.setenv('INVALID_FILE', 'file')
    assert section_name_is_valid('INVALID') is True


def test_incomplete_section_not_returned(monkeypatch):
    monkeypatch.setenv('INVALID_LOG_GROUP_NAME', 'group')
    assert dict(extract_sections_from_env()) == {}
    monkeypatch.setenv('INVALID_FILE', 'file')
    options = copy(SECTION_DEFAULTS)
    options.update({
        'log_group_name': 'group',
        'file': 'file',
    })
    assert dict(extract_sections_from_env()) == {'invalid': options}


@pytest.fixture(scope='session')
def tmpdir(tmpdir_factory):
    return tmpdir_factory.mktemp(str(uuid4()))


@pytest.fixture
def tmpfile(tmpdir):
    return str(tmpdir.join('{}.conf'.format(uuid4())))


@pytest.fixture
def parsed_file(setup, monkeypatch, tmpfile):
    monkeypatch.setenv('CWLOGS_CONFIG_OPTION', 'value')
    cf = ConfigFile(tmpfile, 'state-file')
    cf.autoconfigure()
    cf.write()

    cp = RawConfigParser()
    cp.read(tmpfile)
    return cp


def test_file_sections_present(parsed_file):
    read_sections = sorted(list(sections))
    first_section, *cp_sections = parsed_file.sections()
    assert first_section == 'general'
    assert sorted(cp_sections) == read_sections


def test_file_general(parsed_file):
    assert parsed_file.get('general', 'state_file') == 'state-file'
    assert parsed_file.get('general', 'config_option') == 'value'


@pytest.mark.parametrize("section_name", sections)
def test_file_section(parsed_file, section_name):
    expect_options = options_for_name_defaults(section_name)
    for k, v in expect_options.items():
        assert parsed_file.get(section_name, k) == v
