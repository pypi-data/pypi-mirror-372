# pylint: disable=unused-argument
""" A graphical user interface for WFEngine based on ipywidgets"""
import os
import os.path
import time
import re
from pathlib import Path
from functools import partial
import json
from ruamel import yaml
import ipywidgets as widgets
from ipywidgets import HBox, VBox, Layout
from ipyfilechooser import FileChooser
from IPython.display import display, clear_output, JSON
from fireworks import LaunchPad
from fireworks.user_objects.queue_adapters.common_adapter import CommonAdapter
from fireworks.fw_config import LAUNCHPAD_LOC
from fireworks import Workflow
from prettytable import PrettyTable
from virtmat.middleware.engine.wfengine import WFEngine
from virtmat.middleware.query.wfquery import WFQuery
from virtmat.middleware.engine.wfengine_remote import WFEngineRemote
from virtmat.middleware.exceptions import ConfigurationException
from virtmat.middleware.exceptions import InvalidStateException
from virtmat.middleware.utilities import get_logger
from virtmat.middleware.resconfig import get_default_resconfig, get_resconfig_loc
from virtmat.middleware.resconfig import ResConfig, set_defaults_from_guess


# Getting the arguments with FileChooser and SelectMultiple
lp_file = FileChooser('')
qa_file = FileChooser('')
wf_file = FileChooser('')

style = {'description_width': 'initial'}

# Set default paths for file chooser
HOME = str(Path.home())
fireworks_cfg_dir = os.path.join(HOME, '.fireworks')
lp_file.show_hidden = True
if os.path.exists(fireworks_cfg_dir):
    lp_file.default_path = fireworks_cfg_dir
lp_file.default_filename = 'launchpad.yaml'
qa_file.show_hidden = True
if os.path.exists(fireworks_cfg_dir):
    qa_file.default_path = fireworks_cfg_dir
qa_file.default_filename = 'qadapter.yaml'
wf_file.default_path = os.path.join(HOME)
wf_file.default_filename = 'workflow.yaml'

# Show folder icons for file chooser
lp_file.use_dir_icons = True
qa_file.use_dir_icons = True

# Set multiple file filter patterns for config file
lp_file.filter_pattern = ['*.yaml', '*.json']
qa_file.filter_pattern = ['*.yaml', '*.json']
wf_file.filter_pattern = ['*.yaml', '*.json']

# Set titles for choosers
lp_file.title = 'Select a launchpad file'
qa_file.title = 'Select a qadapter file'
wf_file.title = 'Select a workflow file'

text_input_layout = Layout(width='100%')

configure_button = widgets.Button(tooltip='Create a new and manage running engine',
                                  description='Manage engine', style=style, icon='')
output_configure_button = widgets.Output()

lpad_button = widgets.Button(description='Load launchpad', style=style, icon='upload')
output_lpad_button = widgets.Output()

qadapter_button = widgets.Button(description='Load qadapter', style=style, icon='upload')
output_qadapter_button = widgets.Output()

resconfig_button = widgets.Button(tooltip='Create a new resconfig', style=style,
                                  description='Create resconfig', icon='',
                                  disabled=True)
output_resconfig_button = widgets.Output()

worker_select = widgets.Dropdown(options=[], value=None, description='Workers',
                                 disabled=True)

new_engine_button = widgets.Button(tooltip='New engine will be created',
                                   description='Create new engine', style=style, icon='cogs')
output_new_engine_button = widgets.Output()

dump_engine_button = widgets.Button(tooltip='Save the current engine into a file',
                                    description='Save engine', style=style, icon='download')

resume_engine_button = widgets.Button(tooltip='Load an engine from a file',
                                      description='Load engine', style=style, icon='upload')
output_saveload_engine_button = widgets.Output()

manage_launcher_button = widgets.Button(tooltip='Manage launcher threads',
                                        description='Manage launcher', style=style, icon='')
output_manage_launcher_button = widgets.Output()

start_button = widgets.Button(tooltip='Start a launcher thread in the background',
                              description='Start launcher', style=style, icon='play')
output_start_button = widgets.Output()

stop_button = widgets.Button(tooltip='Stop the launcher thread in the background',
                             description='Stop launcher', style=style, icon='power-off')
output_stop_button = widgets.Output()

manage_workflows_button = widgets.Button(tooltip='Manage workflows', description='Manage workflows',
                                         style=style, icon='')
output_manage_workflows_button = widgets.Output()

new_workflow_button = widgets.Button(tooltip='Add workflows to the engine',
                                     description='Add workflows', style=style, icon='plus')
output_new_workflow_button = widgets.Output()

add_workflow_button = widgets.Button(tooltip='Add workflows from query/file to the engine',
                                     description='Add', style=style, icon='upload')
output_add_workflow_button = widgets.Output()

remove_workflow_button = widgets.Button(tooltip='Remove workflows from the engine',
                                        description='Remove workflows', style=style, icon='trash')
output_remove_workflow_button = widgets.Output()

commit_remove_workflow_button = widgets.Button(tooltip='Remove selected workflows from the engine',
                                               description='Remove', style=style, icon='trash')
output_commit_remove_workflow_button = widgets.Output()

manage_nodes_button = widgets.Button(tooltip='Manage individual workflow nodes',
                                     description='Manage nodes', style=style, icon='')
output_manage_nodes_button = widgets.Output()

status_button = widgets.Button(tooltip='Show the status of all workflows', description='Status',
                               style=style, icon='eye')
nodes_status_button = widgets.Button(tooltip='Show the status of all nodes', description='Status',
                                     style=style, icon='eye')
output_status_button = widgets.Output()

status_button_detail = widgets.Button(tooltip='Show the status of selected nodes',
                                      description='Status', style=style, icon='search-plus')
status_button_detail_output = widgets.Output()

rerun_node_button = widgets.Button(tooltip='Rerun selected nodes', description='Rerun nodes',
                                   style=style, icon='redo')
output_rerun_node_button = widgets.Output()

cancel_launch_button = widgets.Button(tooltip='Cancel the launches of selected nodes',
                                      description='Cancel launches', style=style, icon='xmark')
output_cancel_launch_button = widgets.Output()

update_node_button = widgets.Button(tooltip='Updates the spec dictionaries of selected nodes',
                                    description='Update nodes', style=style, icon='pencil')
output_update_node_button = widgets.Output()

update_rerun_node_button = widgets.Button(tooltip='Updates the selected nodes and reruns them',
                                          description='Update & rerun nodes', style=style)
output_update_rerun_node_button = widgets.Output()

add_nodes_button = widgets.Button(tooltip='Add nodes to a workflow', description='Add nodes',
                                  style=style, icon='plus')
output_add_nodes_button = widgets.Output()

add_node_button = widgets.Button(tooltip='Add the node to the workflow', description='Add node',
                                 style=style, icon='upload')
output_add_node_button = widgets.Output()

query = widgets.Textarea(value='null', placeholder='{}', description='Query',
                         tooltip='PyMongo Query to select workflows (JSON format)',
                         layout=text_input_layout)

wf_query = widgets.VBox([
    widgets.Textarea(value=None, placeholder='{"nodes": {"$in": [1, 2]}, "name": "WF name"}',
                     tooltip='PyMongo Query to select workflows (JSON format)',
                     description='WF query', layout=text_input_layout),
    widgets.Textarea(value=None, placeholder='{"spec.some_value": 4}',
                     tooltip='PyMongo Query to select fireworks (JSON format)',
                     description='FW query', layout=text_input_layout)
])

engine_file = FileChooser('')
engine_file.default_path = '.'
engine_file.use_dir_icons = True
engine_file.filter_pattern = ['*.yaml', '*.json']
engine_file.title = 'WFEngine file'

spec_dict = widgets.Textarea(value=None, description='Update',
                             tooltip='PyMongo spec update query (JSON format)',
                             placeholder='{"key 1": "string", "key 2": [1, 2]}',
                             style={'description_width': 'initial'})

configure_engine_method = widgets.RadioButtons(
    options=['Save or load an existing engine',
             'Create a new engine from scratch'],
    value='Save or load an existing engine',
    description='Method',
    tooltip='Select a method to construct an engine'
)
configure_engine_method_output = widgets.Output()

add_workflow_method = widgets.RadioButtons(options=['From query', 'From file'],
                                           value='From query', description='How to add workflows?',
                                           tooltip='Select the method to add workflows')
output_add_workflow_method = widgets.Output()

pause_restart = widgets.RadioButtons(options=['pause', 'restart'], value='pause',
                                     description='Cancel policy',
                                     tooltip='Select the cancellation policy')

remote_cluster = widgets.Checkbox(value=False, description='Use a remote cluster',
                                  tooltip='Use a remote cluster to launch jobs', indent=False)
remote_cluster_output = widgets.Output()

user_name = widgets.Textarea(value='', placeholder='xy1234', description='Username',
                             tooltip='Username on the remote cluster', layout=text_input_layout)

host_name = widgets.Textarea(value='', placeholder='hostname.domainname', description='Hostname',
                             tooltip='Hostname of the remote cluster', layout=text_input_layout)

remote_conf = widgets.Textarea(value='', placeholder='module load xyz', description='Command',
                               tooltip='Remote configuration command', layout=text_input_layout)

launch_dir = widgets.Textarea(value='', placeholder='/absolute/path/to/launchdir',
                              description='Launchdir',
                              tooltip='Top-level directory in that nodes will be executed',
                              layout=text_input_layout)

unique_launchdir = widgets.Checkbox(value=True,
                                    description='Use unique launch directories',
                                    tooltip='Use unique launch directories')


def clear_consoleoutput():
    """Clear outputs"""
    console_outputs = [output_status_button, output_remove_workflow_button,
                       output_rerun_node_button, output_update_node_button,
                       output_update_rerun_node_button, output_add_nodes_button,
                       output_add_node_button, output_new_workflow_button,
                       output_add_workflow_method, output_add_workflow_button,
                       output_cancel_launch_button, output_stop_button, output_start_button,
                       output_saveload_engine_button]
    for b_out in console_outputs:
        with b_out:
            clear_output()


def clear_button_outputs():
    """Clear top buttons outputs"""
    button_outputs = [output_configure_button, output_manage_launcher_button,
                      output_manage_workflows_button, output_manage_nodes_button]
    for b_out in button_outputs:
        with b_out:
            clear_output()
    clear_consoleoutput()


def configure_button_clicked(bvar):
    """Configure button is clicked"""
    clear_button_outputs()
    with output_configure_button:
        clear_output()
        display(VBox([configure_engine_method,
                      configure_engine_method_output]))
        configure_engine_method_changed(bvar)


def manage_launcher_button_clicked(bvar):
    """manage launcher button is clicked"""
    clear_button_outputs()
    with output_manage_workflows_button:
        clear_output()
        display(HBox([start_button, stop_button]), output_start_button,
                output_stop_button)


def new_workflow_button_clicked(bvar):
    """new workflow button is clicked"""
    clear_consoleoutput()
    with output_new_workflow_button:
        clear_output()
        display(VBox([add_workflow_method, output_add_workflow_method]))
        add_workflow_method_changed(bvar)
        display(add_workflow_button, output_add_workflow_button)


def add_workflow_method_changed(bvar):
    """select the method to add workflows from radio buttons"""
    with output_add_workflow_button:
        clear_output()
    with output_add_workflow_method:
        clear_output()
        if add_workflow_method.value == 'From query':
            print('Using a query to add workflows')
            display(wf_query)
        if add_workflow_method.value == 'From file':
            print('Add workflows from a file')
            display(wf_file)


def remote_cluster_changed(bvar):
    """toggle the remote cluster checkbox"""
    with remote_cluster_output:
        clear_output()
        if remote_cluster.value:
            display(user_name, host_name, remote_conf)


def configure_engine_method_changed(bvar):
    """select engine configuration method from radio buttons"""
    with configure_engine_method_output:
        clear_output()
        if configure_engine_method.value == 'Save or load an existing engine':
            print('Save or load an existing engine')
            display(remote_cluster)
            display(engine_file)
            display(HBox([dump_engine_button, resume_engine_button]),
                    output_saveload_engine_button)
        if configure_engine_method.value == 'Create a new engine from scratch':
            print('Create a new engine from scratch')
            display(lp_file)
            display(lpad_button, output_lpad_button)
            display(resconfig_button, output_resconfig_button)
            display(worker_select)
            cfg = get_default_resconfig()
            if cfg is None:
                resconfig_button.disabled = False
                new_engine_button.disabled = True
            else:
                worker_select.options = [w.name for w in cfg.workers]
                worker_select.value = cfg.default_worker.name
                worker_select.disabled = False
            display(qa_file)
            display(qadapter_button, output_qadapter_button)
            display(query, launch_dir, unique_launchdir)
            display(VBox([remote_cluster, remote_cluster_output]))
            remote_cluster_changed(bvar)
            display(new_engine_button, output_new_engine_button)


def resconfig_button_clicked(bvar):
    """resconfig button is clicked"""
    with output_resconfig_button:
        resconfig_loc = get_resconfig_loc()
        if os.path.exists(resconfig_loc):
            return
        cfg = ResConfig.from_scratch()
        set_defaults_from_guess(cfg.default_worker)
        print('resconfig successfully created')
        cfg.to_file(resconfig_loc)
        print('resconfig successfully saved')
        resconfig_button.disabled = True
        worker_select.options = [w.name for w in cfg.workers]
        worker_select.value = cfg.default_worker.name
        worker_select.disabled = False
        new_engine_button.disabled = False


class WFEnginejupyter():
    """A class for construcing a GUI for FireWorks"""
    wfe = None
    jqadapter = None
    wf_id_select = None
    node_id_select = None
    rows_inputs = None
    rows_outputs = None
    job_category = None
    func_name = None
    size_inp = None
    size_out = None
    logger = get_logger(__name__)

    def __init__(self):
        """Load default launchpad and qadapter"""
        if LAUNCHPAD_LOC:
            try:
                self.jlaunchpad = LaunchPad.from_file(LAUNCHPAD_LOC)
            except FileNotFoundError as error:
                with output_lpad_button:
                    print('The default launchpad file is missing.')
                raise error
            except KeyError as error:
                with output_lpad_button:
                    print('The default lpad file is not correct.')
                raise error
            with output_lpad_button:
                print('Default lpad in ' + LAUNCHPAD_LOC + ' is loaded')

    def new_engine_button_clicked(self, bvar):
        """create new engine button is clicked"""
        with output_new_engine_button:
            clear_output()
        if self.wfe and self.wfe.thread and self.wfe.thread.is_alive():
            self.wfe.stop()
            with output_new_engine_button:
                print('Stopping the running launcher thread, please wait ...')
            self.wfe.thread.join()
            with output_new_engine_button:
                clear_output()
        else:
            query_dict = json.loads(query.value)
            launchdir = launch_dir.value or None
            if remote_cluster.value:
                if host_name.value == '' or user_name.value == '':
                    msg = 'host_name or user_name empty.'
                    raise ConfigurationException(msg)
                if self.jqadapter is None:
                    msg = 'qadapter must be defined in remote cluster mode'
                    raise ConfigurationException(msg)
                self.wfe = WFEngineRemote(launchpad=self.jlaunchpad,
                                          qadapter=self.jqadapter,
                                          wf_query=query_dict,
                                          host=host_name.value,
                                          user=user_name.value,
                                          conf=remote_conf.value,
                                          launchdir=launchdir,
                                          name=worker_select.value,
                                          unique_launchdir=unique_launchdir.value)
                with output_new_engine_button:
                    print('Engine is created for remote launcher')
            else:
                self.wfe = WFEngine(launchpad=self.jlaunchpad,
                                    qadapter=self.jqadapter,
                                    wf_query=query_dict,
                                    launchdir=launchdir,
                                    name=worker_select.value,
                                    unique_launchdir=unique_launchdir.value)
                with output_new_engine_button:
                    print('Engine is created for local launcher')

    def resume_engine_button_clicked(self, bvar):
        """resume engine button is clicked"""
        with output_saveload_engine_button:
            clear_output()
        if self.wfe and self.wfe.thread and self.wfe.thread.is_alive():
            self.wfe.stop()
            with output_saveload_engine_button:
                print('Stopping the running launcher thread, please wait ...')
            self.wfe.thread.join()
        eng_class = WFEngineRemote if remote_cluster.value else WFEngine
        if engine_file.value is None:
            with output_saveload_engine_button:
                print('Select an engine file first.')
            return
        try:
            self.wfe = eng_class.from_file(filename=engine_file.value)
        except (FileNotFoundError, IsADirectoryError) as error:
            with output_saveload_engine_button:
                print('Specify a path to an existing engine file.')
                print(f'Error: {error}')
            raise
        except (PermissionError, json.JSONDecodeError, yaml.YAMLError) as error:
            with output_saveload_engine_button:
                print(f'Error: {error}')
            raise
        except Exception:
            msg = 'An error with loading the engine file ocurred. Check the log for more details.'
            with output_saveload_engine_button:
                print(msg)
            raise
        with output_saveload_engine_button:
            print('An engine has been loaded from file', engine_file.value)

    def dump_engine_button_clicked(self, bvar):
        """dump the engine to file"""
        with output_saveload_engine_button:
            clear_output()
            if self.wfe:
                try:
                    if engine_file.value is None:
                        raise ValueError('Select an engine file first.')
                    self.wfe.to_file(filename=engine_file.value)
                except (FileNotFoundError, IsADirectoryError) as error:
                    print('Specify a valid engine filename or path.')
                    print(error.args)
                except ValueError as error:
                    if 'Unsupported format' in error.args[0]:
                        print('Specify a valid engine filename ending with .json or .yaml')
                        print(error.args)
                    else:
                        print(str(error))
                except PermissionError as error:
                    print(error.args)
                else:
                    print('The engine has been saved in file', engine_file.value)
            else:
                print('Create an engine first.')

    def lpad_button_clicked(self, bvar):
        """load user defined launchpad"""
        with output_lpad_button:
            clear_output()
            if lp_file.selected is None:
                print('Select a launchpad file.')
                time.sleep(1)
                return
            try:
                self.jlaunchpad = LaunchPad.from_file(lp_file.selected)
            except FileNotFoundError as error:
                print('Select a valid launchpad file')
                print(error.args)
            else:
                print('Launchpad has been loaded from file', lp_file.selected)

    def qadapter_button_clicked(self, bvar):
        """load user defined qadapter"""
        with output_qadapter_button:
            clear_output()
            if qa_file.selected is None:
                print('Select a qadapter file.')
                time.sleep(1)
                return
            try:
                self.jqadapter = CommonAdapter.from_file(qa_file.selected)
            except FileNotFoundError as error:
                print('Select a valid qadapter file')
                print(error.args)
            else:
                print('Qadapter has been loaded from file', qa_file.selected)

    def start_launcher_clicked(self, bvar):
        """start launcher button clicked"""
        clear_consoleoutput()
        try:
            self.wfe.start()
        except Exception as err:
            with output_start_button:
                print(f'Error occurred: {err}')
            raise
        with output_start_button:
            clear_output()
            print('The launcher thread is created.')

    def stop_launcher_clicked(self, bvar):
        """stop launcher button clicked"""
        clear_consoleoutput()
        with output_stop_button:
            clear_output()
            try:
                self.wfe.stop()
                print('please wait ...')
                self.wfe.thread.join()
                clear_output()
                print('Launcher thread is stopped.')
            except AttributeError:
                print('There is no running thread.')

    def manage_workflows_button_clicked(self, bvar):
        """manage workflows button is clicked"""
        clear_button_outputs()
        with output_manage_workflows_button:
            clear_output()
            display(HBox([status_button, new_workflow_button,
                          remove_workflow_button]), output_status_button,
                    output_new_workflow_button, output_remove_workflow_button)

    def status_button_clicked(self, bvar):
        """workflow status summary"""
        clear_consoleoutput()
        with output_status_button:
            clear_output()
            self.wfe.show_wf_status(add_io_info=False)

    def add_workflow_button_clicked(self, bvar):
        """add workflows from a query or a file"""
        with output_add_workflow_button:
            clear_output()
        if add_workflow_method.value == 'From file':
            if wf_file.selected is None:
                with output_add_workflow_button:
                    print('Select a workflow file first')
                return
            try:
                with open(wf_file.selected, 'rt', encoding='utf-8') as wff:
                    wf_obj = yaml.safe_load(wff)
            except FileNotFoundError as err:
                with output_add_workflow_button:
                    print('Specify a path to an existing workflow file.')
                    print(f'Error: {err}')
                raise
            except Exception:
                msg = 'An error occurred loading the workflow file. Check the logs for details.'
                with output_add_workflow_button:
                    print(msg)
                raise
            if isinstance(wf_obj, dict):
                wf_lst = [wf_obj]
            elif isinstance(wf_obj, list):
                wf_lst = wf_obj
            else:
                msg = 'The workflow file must contain either a dict or a list.'
                with output_add_workflow_button:
                    print(f'Error: {msg}')
                raise TypeError(msg)
            try:
                for wf_dct in wf_lst:
                    self.wfe.add_workflow(workflow=Workflow.from_dict(wf_dct))
            except Exception as err:
                with output_add_workflow_button:
                    print(f'Error: {err}')
                raise
            msg = f'{len(wf_lst)} workflow(s) have been loaded from file {wf_file.selected}'
            with output_add_workflow_button:
                print(msg)
        elif add_workflow_method.value == 'From query':
            try:
                wfq_dct = json.loads(wf_query.children[0].value)
                if not isinstance(wfq_dct, dict):
                    raise ValueError('The WF query must be a dictionary')
                fwq_dct = json.loads(wf_query.children[1].value)  # pylint: disable=E1136
                if not isinstance(fwq_dct, dict):
                    raise ValueError('The FW query must be a dictionary')
            except (ValueError, json.JSONDecodeError) as err:
                with output_add_workflow_button:
                    print(f'Error: {str(err)}')
                raise
            wfq = WFQuery(self.wfe.launchpad, wfq_dct, fwq_dct, metadata_only=True)
            with output_add_workflow_button:
                print(f'Adding the workflow IDs: {wfq.get_wf_ids()}')
            for wf_id in wfq.get_wf_ids():
                try:
                    self.wfe.add_workflow(fw_id=wf_id)
                except ConfigurationException as err:
                    with output_add_workflow_button:
                        print(f'{str(err)} {wf_id}')
                    raise
                with output_add_workflow_button:
                    print(f'Workflow {wf_id} has been loaded from query ')

    def create_wf_id_select(self):
        """creates a new selector with updated workflow ids"""
        self.wf_id_select = widgets.SelectMultiple(
            options=self.wfe.wf_ids,
            value=[],
            description='Workflow IDs',
            disabled=False
        )

    def remove_workflow_button_clicked(self, bvar):
        """remove workflows from engine"""
        clear_consoleoutput()
        with output_commit_remove_workflow_button:
            clear_output()
        self.create_wf_id_select()
        with output_remove_workflow_button:
            display(self.wf_id_select)
            display(commit_remove_workflow_button, output_commit_remove_workflow_button)

    def commit_remove_workflow_button_clicked(self, bvar):
        """commit workflows removal from engine"""
        with output_commit_remove_workflow_button:
            clear_output()
            for wf_id in self.wf_id_select.value:
                self.wfe.remove_workflow(wf_id)
            print(f'{len(self.wf_id_select.value)} workflow(s) removed')
        self.create_wf_id_select()
        with output_remove_workflow_button:
            clear_output()
            display(self.wf_id_select)
            display(commit_remove_workflow_button, output_commit_remove_workflow_button)

    def manage_nodes_button_clicked(self, bvar):
        """Manage nodes button is clicked"""
        self.node_id_select = widgets.SelectMultiple(
            options=self.wfe.fw_ids,
            value=[],
            description='Node IDs',
            disabled=False
        )
        clear_button_outputs()
        with output_manage_nodes_button:
            clear_output()
            display(HBox([self.node_id_select, spec_dict, pause_restart]))
            display(HBox([nodes_status_button, status_button_detail,
                          rerun_node_button, update_node_button,
                          update_rerun_node_button, cancel_launch_button,
                          add_nodes_button]),
                    output_status_button, status_button_detail_output,
                    output_rerun_node_button, output_update_node_button,
                    output_update_rerun_node_button, output_cancel_launch_button,
                    output_add_nodes_button)

    def nodes_status_button_clicked(self, bvar):
        """nodes status summary"""
        clear_consoleoutput()
        with output_status_button:
            clear_output()
            self.wfe.show_nodes_status()
        exp_time = 14400
        lost_runs = self.wfe.get_lost_jobs(time=exp_time)
        if len(lost_runs) != 0:
            with output_status_button:
                print(f'\nRunning nodes not been updated within {exp_time} s')
                print(lost_runs)

        unres_nodes = self.wfe.get_unreserved_nodes(time=exp_time)
        if len(unres_nodes) != 0:
            columns = unres_nodes[0].keys()
            table = PrettyTable(columns)
            for node in unres_nodes:
                table.add_row([node[c] for c in columns])
            with output_status_button:
                print(f'\nReserved nodes not been updated within {exp_time} s')
                print(table)

    def status_detailed_button_clicked(self, bvar):
        """status details about selected nodes"""
        clear_consoleoutput()
        lst = self.wfe.status_detail(*self.node_id_select.value)
        with output_status_button:
            display(JSON(lst))

    def rerun_node_button_clicked(self, bvar):
        """rerun selected nodes and print their new status"""
        clear_consoleoutput()
        for node in self.node_id_select.value:
            try:
                self.wfe.rerun_node(node)
            except InvalidStateException as err:
                with output_rerun_node_button:
                    print(err)
            except Exception as err:
                with output_rerun_node_button:
                    print('Unknown error. Check the logs.')
                raise err
            else:
                with output_rerun_node_button:
                    print(f'Node ID {node} has been rerun.')

    def update_node_button_clicked(self, bvar):
        """update selected nodes"""
        clear_consoleoutput()
        try:
            dct = json.loads(spec_dict.value)
        except json.JSONDecodeError as jerr:
            with output_update_node_button:
                print(jerr)
        else:
            for node in self.node_id_select.value:
                try:
                    self.wfe.update_node(node, dct)
                except InvalidStateException as err:
                    with output_update_node_button:
                        print(err)
                except Exception as err:
                    with output_update_node_button:
                        print('Unknown error. Check the logs.')
                        print(err)
                    raise err
                else:
                    with output_update_node_button:
                        print(f'Node ID {node} has been updated.')

    def update_rerun_node_button_clicked(self, bvar):
        """update and rerun selected nodes"""
        clear_consoleoutput()
        try:
            dct = json.loads(spec_dict.value)
        except json.JSONDecodeError as jerr:
            with output_update_rerun_node_button:
                print(jerr)
        else:
            for node in self.node_id_select.value:
                try:
                    self.wfe.update_rerun_node(node, dct)
                except InvalidStateException as err:
                    with output_update_rerun_node_button:
                        print(err)
                except Exception as err:
                    with output_update_rerun_node_button:
                        print('Unknown error. Check the logs.')
                        print(err)
                    raise err
                else:
                    with output_update_rerun_node_button:
                        print(f'Node ID {node} has been updated and rerun.')

    def add_nodes_button_clicked(self, bvar):
        """add nodes button is clicked"""
        clear_consoleoutput()

        def get_input_row():
            dropdown_kwargs = {'options': self.wfe.fw_ids, 'value': None,
                               'description': 'Node ID', 'disabled': False}
            while True:
                name_widget = widgets.Text(description='Name')
                value_widget = widgets.Text(description='Value', value='null')
                node_id_widget = widgets.Dropdown(**dropdown_kwargs)
                yield [name_widget, value_widget, node_id_widget]

        get_input_row_iter = get_input_row()

        def on_value_change(change, wids, wout, wtype=None):
            wout.clear_output()
            size = change['new']
            if size <= len(wids):
                wids = wids[:size]
            else:
                nadd = size - len(wids)
                if wtype == 'inputs':
                    elems = next(get_input_row_iter)
                    wids.extend([widgets.HBox(elems)]*nadd)
                elif wtype == 'outputs':
                    wids.extend([widgets.Text(description='Name')]*nadd)
            with wout:
                display(widgets.VBox(wids))

        self.rows_inputs = [widgets.HBox(next(get_input_row_iter))]
        output_inputs = widgets.Output()
        self.rows_outputs = [widgets.Text(description='Name')]
        output_outputs = widgets.Output()
        radio_kwargs = {'options': ['interactive', 'batch', 'remote'],
                        'value': 'interactive', 'description': 'Job category',
                        'tooltip': 'Select job category'}
        self.job_category = widgets.RadioButtons(**radio_kwargs)
        self.func_name = widgets.Text(description='Function', value=None, placeholder='math.log',
                                      tooltip='Fully qualified name of a Python function')
        self.size_inp = widgets.BoundedIntText(value=1, min=0, description='# Inputs')
        self.size_out = widgets.BoundedIntText(value=1, min=0, description='# Outputs')
        self.size_inp.observe(partial(on_value_change, wids=self.rows_inputs,
                              wout=output_inputs, wtype='inputs'), 'value')
        self.size_out.observe(partial(on_value_change, wids=self.rows_outputs,
                              wout=output_outputs, wtype='outputs'), 'value')
        with output_add_nodes_button:
            display(self.func_name)
            display(self.size_inp)
            display(output_inputs)
            display(self.size_out)
            display(output_outputs)
            display(self.job_category)
            display(add_node_button, output_add_node_button)
            with output_inputs:
                display(widgets.VBox(self.rows_inputs))
            with output_outputs:
                display(widgets.VBox(self.rows_outputs))

    def add_node_button_clicked(self, bvar):
        """add node button is clicked"""
        output_add_node_button.clear_output()
        id_pattern = r'[^\d\W]\w*\b'
        inputs = []
        outputs = []
        try:
            if not re.match(r'^'+id_pattern+r'(\.'+id_pattern+r')*$', self.func_name.value):
                raise ValueError(f'Invalid function name: {self.func_name.value}')
            for row in self.rows_inputs[:self.size_inp.value]:
                input_name = row.children[0].value
                if not re.match(r'^'+id_pattern+r'$', input_name):
                    raise ValueError(f'Input name not valid: {input_name}')
                input_val = json.loads(row.children[1].value)
                input_node_id = row.children[2].value
                inputs.append((input_node_id, input_name, input_val))
            for row in self.rows_outputs[:self.size_out.value]:
                output_val = row.value
                if not re.match(r'^'+id_pattern+r'$', output_val):
                    raise ValueError(f'Output name not valid: {output_val}')
                outputs.append(output_val)
        except (ValueError, json.JSONDecodeError) as err:
            with output_add_node_button:
                print(f'Error: {str(err)}')
            raise err
        self.wfe.add_node(func=self.func_name.value, inputs=inputs,
                          outputs=outputs, category=self.job_category.value)
        with output_add_node_button:
            print('Added a new node.')

    def cancel_launch_button_clicked(self, bvar):
        """cancel launched (reserved or running) nodes"""
        clear_consoleoutput()
        with output_cancel_launch_button:
            clear_output()
        cancel_kwargs = {pause_restart.value: True}
        for fw_id in self.node_id_select.value:
            try:
                self.wfe.cancel_job(fw_id, **cancel_kwargs)
            except (InvalidStateException, ConfigurationException) as err:
                with output_cancel_launch_button:
                    print(err)
            except Exception as err:
                with output_cancel_launch_button:
                    print('Unknown error. Check the logs.', err)
                raise
            else:
                with output_cancel_launch_button:
                    print(f'Launch of node {fw_id} has been cancelled.')


wfengine = WFEnginejupyter()

new_engine_button.on_click(wfengine.new_engine_button_clicked)
resume_engine_button.on_click(wfengine.resume_engine_button_clicked)
resconfig_button.on_click(resconfig_button_clicked)
configure_button.on_click(configure_button_clicked)
new_workflow_button.on_click(new_workflow_button_clicked)
lpad_button.on_click(wfengine.lpad_button_clicked)
qadapter_button.on_click(wfengine.qadapter_button_clicked)
start_button.on_click(wfengine.start_launcher_clicked)
stop_button.on_click(wfengine.stop_launcher_clicked)
status_button.on_click(wfengine.status_button_clicked)
nodes_status_button.on_click(wfengine.nodes_status_button_clicked)
status_button_detail.on_click(wfengine.status_detailed_button_clicked)
dump_engine_button.on_click(wfengine.dump_engine_button_clicked)
manage_launcher_button.on_click(manage_launcher_button_clicked)
manage_workflows_button.on_click(wfengine.manage_workflows_button_clicked)
add_workflow_button.on_click(wfengine.add_workflow_button_clicked)
remove_workflow_button.on_click(wfengine.remove_workflow_button_clicked)
commit_remove_workflow_button.on_click(wfengine.commit_remove_workflow_button_clicked)
manage_nodes_button.on_click(wfengine.manage_nodes_button_clicked)
rerun_node_button.on_click(wfengine.rerun_node_button_clicked)
update_node_button.on_click(wfengine.update_node_button_clicked)
update_rerun_node_button.on_click(wfengine.update_rerun_node_button_clicked)
add_nodes_button.on_click(wfengine.add_nodes_button_clicked)
add_node_button.on_click(wfengine.add_node_button_clicked)
cancel_launch_button.on_click(wfengine.cancel_launch_button_clicked)
remote_cluster.observe(remote_cluster_changed)
configure_engine_method.observe(configure_engine_method_changed)
add_workflow_method.observe(add_workflow_method_changed)

display(HBox([configure_button, manage_launcher_button,
              manage_workflows_button, manage_nodes_button]),
        output_configure_button, output_manage_launcher_button,
        output_manage_workflows_button, output_manage_nodes_button)
