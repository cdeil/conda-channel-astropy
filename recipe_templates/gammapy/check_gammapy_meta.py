#!/usr/bin/env python
import logging
from collections import OrderedDict
from astropy.extern.six.moves.configparser import SafeConfigParser
import yaml

log = logging.getLogger(__name__)
logging.basicConfig(level='INFO')


class GammapyCondaMetaChecker:
    """
    Check if Gammapy conda recipe is up to date.

    See https://github.com/astropy/conda-channel-astropy/blob/master/recipe_templates/gammapy/meta.yaml

    TODO:
    - Add other checks, e.g. `requirements/run` should be consistent with `setup.py`
    - For now, I'm logging issues. Is there a need to record them in `results` instead?
    """

    def __init__(self, conda_meta_filename, setup_cfg_filename):
        self.conda_meta = self._read_conda_meta(conda_meta_filename)
        self.setup_cfg = self._read_setup_cfg(setup_cfg_filename)
        self.results = OrderedDict()

    @staticmethod
    def _read_conda_meta(filename):
        with open(filename) as fh:
            # return yaml.load(fh)
            meta = fh.read()

        meta = meta.replace('{{ ', '{').replace(' }}', '}')
        meta = meta.format(version='dummy', md5='dummy')
        return yaml.load(meta)

    @staticmethod
    def _read_setup_cfg(filename):
        parser = SafeConfigParser()
        parser.read(filename)
        return parser

    def check_entry_points(self):
        """Check if the ``test/entry_points`` list is OK."""
        log.info('*** Checking entry_points')

        # entry_points_conda = OrderedDict()
        # for line in self.conda_meta['build']['entry_points']:
        #     key, val = line.split('=')
        #     entry_points_conda[key.strip()] = val.strip()
        # entry_points_setup = OrderedDict(self.setup_cfg['entry_points'])
        # for key, val in entry_points_conda.items():
        #     if key not in entry_points_setup:
        #         log.error('Inconsistent entry point:')

        entry_points_conda = self.conda_meta['build']['entry_points']
        entry_points_setup = ['{} = {}'.format(k, v) for k, v in self.setup_cfg['entry_points'].items()]
        # print(entry_points_conda)
        # print(entry_points_setup)
        # import IPython; IPython.embed()

        for item in set(entry_points_conda) - set(entry_points_setup):
            log.error('Entry point in conda, but not in setup: {}'.format(item))

        for item in set(entry_points_setup) - set(entry_points_conda):
            log.error('Entry point in setup, but not in conda: {}'.format(item))

        results = OrderedDict()
        self.results['entry_points'] = results

    def check_imports(self):
        """Check if the ``test/imports`` list is OK."""
        imports_meta = self.conda_meta['test']['imports']
        print(imports_meta)

        results = OrderedDict()
        self.results['imports'] = results

    def check_commands(self):
        """Check if the ``test/commands`` list is OK."""
        commands_meta = self.conda_meta['test']['commands']
        commands_setup = list(self.setup_cfg['entry_points'])
        print(commands_meta)
        print(commands_setup)

        results = OrderedDict()
        self.results['commands'] = results

    def print_results(self):
        """Pretty-print the results dict"""
        print(yaml.dump(self.results, default_flow_style=False))


if __name__ == '__main__':
    conda_meta_filename = '/Users/deil/code/conda-channel-astropy/recipe_templates/gammapy/meta.yaml'
    setup_cfg_filename = '/Users/deil/code/gammapy/setup.cfg'
    checker = GammapyCondaMetaChecker(
        conda_meta_filename=conda_meta_filename,
        setup_cfg_filename=setup_cfg_filename,
    )
    checker.check_entry_points()
    checker.check_imports()
    checker.check_commands()
    # checker.print_results()
