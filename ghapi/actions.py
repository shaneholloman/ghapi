# AUTOGENERATED! DO NOT EDIT! File to edit: 01_actions.ipynb (unless otherwise specified).

__all__ = ['contexts', 'context_github', 'context_env', 'context_job', 'context_steps', 'context_runner',
           'context_secrets', 'context_strategy', 'context_matrix', 'context_needs', 'env_github', 'user_repo', 'Event',
           'create_workflow_files', 'fill_workflow_templates', 'env_contexts', 'def_pipinst', 'create_workflow',
           'gh_create_workflow', 'example_payload', 'github_token', 'actions_output', 'actions_debug', 'actions_warn',
           'actions_error', 'actions_group', 'actions_mask', 'set_git_user']

# Cell
from fastcore.utils import *
from fastcore.script import *
from fastcore.foundation import *
from fastcore.meta import *
from .core import *
from .templates import *

import textwrap
from contextlib import contextmanager
from enum import Enum

# Cell
# So we can run this outside of GitHub actions too, read from file if needed
for a,b in (('CONTEXT_GITHUB',context_example), ('CONTEXT_NEEDS',needs_example), ('GITHUB_REPOSITORY','octocat/Hello-World')):
    if a not in os.environ: os.environ[a] = b

contexts = 'github', 'env', 'job', 'steps', 'runner', 'secrets', 'strategy', 'matrix', 'needs'
for context in contexts:
    globals()[f'context_{context}'] = dict2obj(loads(os.getenv(f"CONTEXT_{context.upper()}", "{}")))

# Cell
#nbdev_comment _all_ = ['context_github', 'context_env', 'context_job', 'context_steps', 'context_runner', 'context_secrets', 'context_strategy', 'context_matrix', 'context_needs']

# Cell
env_github = dict2obj({k[7:].lower():v for k,v in os.environ.items() if k.startswith('GITHUB_')})

# Cell
def user_repo():
    "List of `user,repo` from `env_github.repository"
    return env_github.repository.split('/')

# Cell
Event = str_enum('Event',
    'page_build','content_reference','repository_import','create','workflow_run','delete','organization','sponsorship',
    'project_column','push','context','milestone','project_card','project','package','pull_request','repository_dispatch',
    'team_add','workflow_dispatch','member','meta','code_scanning_alert','public','needs','check_run','security_advisory',
    'pull_request_review_comment','org_block','commit_comment','watch','marketplace_purchase','star','installation_repositories',
    'check_suite','github_app_authorization','team','status','repository_vulnerability_alert','pull_request_review','label',
    'installation','release','issues','repository','gollum','membership','deployment','deploy_key','issue_comment','ping',
    'deployment_status','fork','schedule')

# Cell
def _create_file(path:Path, fname:str, contents):
    if contents and not (path/fname).exists(): (path/fname).write_text(contents)

def _replace(s:str, find, repl, i:int=0, suf:str=''):
    return s.replace(find, textwrap.indent(repl, ' '*i)+suf)

# Cell
def create_workflow_files(fname:str, workflow:str, build_script:str, prebuild:bool=False):
    "Create workflow and script files in suitable places in `github` folder"
    if not os.path.exists('.git'): return print('This does not appear to be the root of a git repo')
    wf_path  = Path('.github/workflows')
    scr_path = Path('.github/scripts')
    wf_path .mkdir(parents=True, exist_ok=True)
    scr_path.mkdir(parents=True, exist_ok=True)
    _create_file(wf_path, f'{fname}.yml', workflow)
    _create_file(scr_path, f'build-{fname}.py', build_script)
    if prebuild: _create_file(scr_path, f'prebuild-{fname}.py', build_script)

# Cell
def fill_workflow_templates(name:str, event, run, context, script, opersys='ubuntu', prebuild=False):
    "Function to create a simple Ubuntu workflow that calls a Python `ghapi` script"
    c = wf_tmpl
    if event=='workflow_dispatch:': event=''
    needs = '    needs: [prebuild]' if prebuild else None
    for find,repl,i in (('NAME',name,0), ('EVENT',event,2), ('RUN',run,8), ('CONTEXTS',context,8),
                       ('OPERSYS',f'[{opersys}]',0), ('NEEDS',needs,0), ('PREBUILD',pre_tmpl if prebuild else '',2)):
        c = _replace(c, f'${find}', str(repl), i)
    create_workflow_files(name, c, script, prebuild=prebuild)

# Cell
def env_contexts(contexts):
    "Create a suitable `env:` line for a workflow to make a context available in the environment"
    contexts = uniqueify(['github'] + listify(contexts))
    return "\n".join("CONTEXT_" + o.upper() + ": ${{ toJson(" + o.lower() + ") }}" for o in contexts)

# Cell
def_pipinst = 'pip install -Uq ghapi'

# Cell
def create_workflow(name:str, event:Event, contexts:list=None, opersys='ubuntu', prebuild=False):
    "Function to create a simple Ubuntu workflow that calls a Python `ghapi` script"
    script = "from fastcore.all import *\nfrom ghapi import *"
    fill_workflow_templates(name, f'{event}:', def_pipinst, env_contexts(contexts),
                            script=script, opersys=opersys, prebuild=prebuild)

# Cell
@call_parse
def gh_create_workflow(
    name:Param("Name of the workflow file", str),
    event:Param("Event to listen for", str),
    contexts:Param("Space-delimited extra contexts to include in `env` in addition to 'github'", str)=''
):
    "Supports `gh-create-workflow`, a CLI wrapper for `create_workflow`."
    create_workflow(name, Event[event], contexts.split())

# Cell
_example_url = 'https://raw.githubusercontent.com/fastai/ghapi/master/examples/{}.json'

# Cell
def example_payload(event):
    "Get an example of a JSON payload for `event`"
    return dict2obj(urljson(_example_url.format(event)))

# Cell
def github_token():
    "Get GitHub token from `GITHUB_TOKEN` env var if available, or from `github` context"
    return os.getenv('GITHUB_TOKEN', context_github.get('token', None))

# Cell
def actions_output(name, value):
    "Print the special GitHub Actions `::set-output` line for `name::value`"
    print(f"::set-output name={name}::{value}")

# Cell
def actions_debug(message):
    "Print the special `::debug` line for `message`"
    print(f"::debug::{message}")

# Cell
def actions_warn(message, details=''):
    "Print the special `::warning` line for `message`"
    print(f"::warning {details}::{message}")

# Cell
def actions_error(message, details=''):
    "Print the special `::error` line for `message`"
    print(f"::error {details}::{message}")

# Cell
@contextmanager
def actions_group(title):
    "Context manager to print the special `::group`/`::endgroup` lines for `title`"
    print(f"::group::{title}")
    yield
    print(f"::endgroup::")

# Cell
def actions_mask(value):
    "Print the special `::add-mask` line for `value`"
    print(f"::add-mask::{value}")

# Cell
def set_git_user(api=None):
    "Set git user name/email to authenticated user (if `api`) or GitHub Actions bot (otherwise)"
    if api:
        user  = api.users.get_authenticated().name
        email = first(api.users.list_emails_for_authenticated(), attrgetter('primary')).email
    else:
        user  = 'github-actions[bot]'
        email = 'github-actions[bot]@users.noreply.github.com'
    run(f'git config --global user.email "{email}"')
    run(f'git config --global user.name  "{user}"')