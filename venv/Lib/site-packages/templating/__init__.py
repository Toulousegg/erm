import argparse
import yaml
import os
import logging
import copy
import jinja2
import sys
import collections
import importlib
from jsonschema import validate as validate_schema

instance_schema = {
    "type": "array",
    "minItems": 1,
    "items": [
        {
            "type": "object"
        },
        {
            "type": "string"
        }
    ]
}

config_schema = {
    'plugins': {
        'type': 'array'
    },
    'defaults': {
        'type': 'object'
    },
    'config': {
        'type': 'object'
    },
    'templates': {
        'oneOf': [
            {
                'type': 'object'
            },
            {
                'type': 'array'
            }
        ]
    },
    'instances': instance_schema
}


def deep_update(d, u):
   if u is None:
       return d

   for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = deep_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
   return d


class Config(object):
    logger = logging.getLogger('templating.Config')

    def __init__(self, filehandle):
        self._config = yaml.load(filehandle)

        self.logger.debug('Config: %s', self._config)

        if 'defaults' not in self._config:
            self._config['defaults'] = {}

        if 'config' not in self._config:
            self._config['config'] = {}

        if 'templates' not in self._config:
            self._config['templates'] = {}

        if 'plugins' not in self._config:
            self._config['plugins'] = []

        instances = {}
        for instance in self._config.get('instances', []):
            if type(instance) is str:
                instances[instance] = {}
            elif type(instance) is dict:
                key, value = next(iter(instance.items()))
                instances[key] = value

        self._config['instances'] = instances

        validate_schema(self._config, config_schema)

    @property
    def defaults(self):
        return self._config['defaults']

    @property
    def config(self):
        return self._config['config']

    @property
    def templates(self):
        return self._config['templates']

    @property
    def instances(self):
        return self._config['instances']

    @property
    def plugins(self):
        return self._config['plugins']

    def __str__(self):
        return yaml.dump(self._config)


class Instance(object):
    logger = logging.getLogger('templating.Instance')

    @classmethod
    def create_instance(cls, instance_name, config, env):
        defaults = copy.deepcopy(config.defaults)
        deep_update(defaults, config.instances[instance_name])

        return cls(instance_name, defaults, env)

    def __init__(self, name, context=None, env=None):
        if context:
            context.update(instance=name)
            self._context = context
        else:
            self._context = {'instance': name}

        if env:
            self._env = env
        else:
            self._env = jinja2.Environment()

    def render_template_name(self, template_name):
        return self._env.from_string(template_name).render(**self._context)

    def render(self, template_path):
        self.logger.debug('Instance context: %s', self._context)
        with open(template_path) as fh:
            return self._env.from_string(fh.read()).render(**self._context)

    def __str__(self):
        return yaml.dump(self._context)


def discover_config(path=None, logger=logging.getLogger('templating.discover_config')):
    logger.debug('Searching for config, %s', path)
    if path:
        path = os.path.expanduser(path)
        logger.debug('Expanding path: %s', path)
        path = os.path.abspath(path)
        logger.debug('Abs path: %s', path)
        if os.path.exists(path):
            logger.info('Found config: %s', path)
            return path
        else:
            return None

    paths = [
        './templating.yaml',
        '~/.templating.yaml'
    ]

    for path in paths:
        path = os.path.expanduser(path)
        logger.debug('Expanding path: %s', path)
        path = os.path.abspath(path)
        logger.debug('Abs path: %s', path)
        if os.path.exists(path):
            logger.info('Found config: %s', path)
            return path

    logger.error('No config file found.')


def create_directories(path):
    path, _ = os.path.split(path)
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except FileNotFoundError:
            create_directories(path)
            os.mkdir(path)


def main():
    logger = logging.getLogger(__name__)
    log_format = "%(asctime)-15s %(name)-8s:%(funcName)s [%(levelname)6s] %(message)s"
    logging_choices = {
        'DEBUG': logging.DEBUG,
        'ERROR': logging.ERROR,
        'WARN': logging.WARN,
        'INFO': logging.INFO
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log-level', dest='logging_level', choices=logging_choices.keys(),
                        default='INFO', help='logging level')
    parser.add_argument('-c', '--config', default=None, help="Config to use.")
    parser.add_argument('-i', '--instance', default=None, help="Instance to render, defaults to all")

    args = parser.parse_args()

    log_level = logging_choices[args.logging_level]

    logging.basicConfig(level=log_level, format=log_format)

    config_path = discover_config(args.config)


    if config_path is None:
        return 1

    with open(config_path) as fh:
        config = Config(fh)

    # allow custom template tags

    kwargs = {}
    for setting in [ 'block_start_string', 'block_end_string', 'variable_start_string', 'variable_end_string',
                      'comment_start_string', 'comment_end_string']:
        if setting in config.config:
            val = str(config.config[setting])
            kwargs[setting] = val

    env = jinja2.Environment(**kwargs)

    if args.instance:
        instance_name = args.instance
        instances = [ Instance.create_instance(instance_name, config, env) ]
    else:
        instances = [
            Instance.create_instance(name, config, env) for name in config.instances
        ]

    output_dir = config.config.get('output_dir', None)

    if output_dir:
        output_dir = os.path.abspath(output_dir)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        elif not os.path.isdir(output_dir):
            logger.error('Output dir is not a directory %s', output_dir)
            return 1


    # load plugins
    for plugin_name in config.plugins:
        try:
            plugin = importlib.import_module(plugin_name)
        except ImportError as e:
            logger.error("Failed to import plugin: %s", plugin_name)
            logger.exception(e)
            return 1
        else:
            try:
              plugin.init(env)
            except AttributeError:
              logger.error("Failed to call %s.init, method not found", plugin_name)
              return 1


    for name, template in config.templates.items():
        for instance in instances:
            rendered_name = instance.render_template_name(name)
            template = instance.render_template_name(template)
            dest = os.path.join(config.config.get('output_dir', ''), rendered_name)
            if not os.path.exists(dest):
                create_directories(dest)
            logger.info('Rendering %s to %s', template, dest)
            with open(dest, 'w+') as fh:
                fh.write(instance.render(template))

    return 0

if __name__ == "__main__":
    sys.exit(main())
