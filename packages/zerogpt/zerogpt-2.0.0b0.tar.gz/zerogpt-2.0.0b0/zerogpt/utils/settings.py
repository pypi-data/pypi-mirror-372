class Settings:
    def __init__(self):
        self.state = {
            'keep-alive': {'enabled': True},
            'local_address': {'enabled': True, 'address': '0.0.0.0'},
            'retries': {'enabled': True, 'retries': 3},
            'pre-warm': {'enabled': True},
            'retry stream': {'enabled': True, 'retries': 6}
        }

    def disable(self, option):
        option_key = option.lower()
        opts = self.options()
        if option_key not in self.state:
            return {'status': 'Option not found'}
        if not opts.get(option_key, {}).get('can_disable', False):
            return {'status': 'This option cannot be disabled'}
        if not self.state[option_key].get('enabled', True):
            return {'status': 'Already disabled'}
        self.state[option_key]['enabled'] = False
        return {'status': 'Disabled'}

    def enable(self, option):
        option_key = option.lower()
        opts = self.options()
        if option_key not in self.state:
            return {'status': 'Option not found'}
        if self.state[option_key].get('enabled', True):
            return {'status': 'Already enabled'}
        if not opts.get(option_key, {}).get('can_disable', False):
            return {'status': 'This option cannot be disabled/enabled'}
        self.state[option_key]['enabled'] = True
        return {'status': 'Enabled'}

    def change(self, option, **kwargs):
        option_key = option.lower()
        opts = self.options()
        if option_key not in self.state:
            return {'status': 'Option not found'}
        if not opts.get(option_key, {}).get('can_change', False):
            return {'status': 'This option cannot be changed'}
        allowed_kwargs = opts[option_key].get('kwargs')
        if not allowed_kwargs:
            return {'status': 'No parameters to change'}

        for k, v in kwargs.items():
            if k not in allowed_kwargs:
                return {'status': f'Parameter {k} not allowed to change'}
            expected_type = allowed_kwargs[k]['value_type']
            if expected_type == 'int' and not isinstance(v, int):
                return {'status': f'Parameter {k} must be int'}
            if expected_type == 'str' and not isinstance(v, str):
                return {'status': f'Parameter {k} must be str'}

            self.state[option_key][k] = v

        return {'status': 'Changed', 'new_state': self.state[option_key]}

    def options(self):
        return {
            'keep-alive': {
                'default': 'Enabled',
                'can_disable': False,
                'can_change': False,
                'kwargs': None
            },
            'local_address': {
                'default': 'Enabled',
                'can_disable': True,
                'can_change': True,
                'kwargs': {
                    'address': {
                        'example': ['0.0.0.0', 'your address'],
                        'value_type': 'str'
                    }
                }
            },
            'retries': {
                'default': 'Enabled',
                'can_disable': True,
                'can_change': True,
                'kwargs': {
                    'retries': {
                        'example': [3, 6, 9],
                        'value_type': 'int'
                    }
                }
            },
            'pre-warm': {
                'default': 'Enabled',
                'can_disable': True,
                'can_change': False,
                'kwargs': None
            },
            'retry stream': {
                'default': 'Enabled',
                'can_disable': False,
                'can_change': True,
                'kwargs': {
                    'retries': {
                        'example': [3, 6, 9],
                        'value_type': 'int'
                    }
                }
            },
            'resume': {
                'default': 'Enabled',
                'can_disable': False,
                'can_change': False,
            }
        }

settings = Settings()