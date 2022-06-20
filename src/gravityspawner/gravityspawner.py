from jupyterhub.spawner import LocalProcessSpawner, Spawner
from traitlets import (
    Type, Tuple, List, Dict, Unicode
)
from wrapspawner import WrapSpawner

class GravitySpawner(WrapSpawner):
    """GravitySpawner: changed from ProfilesSpawner, thanks wrapspawner.ProfilesSpawner!
        - in addition to select PBS/Slurm queue, we still wanna set time, memory, CPU cores etc.
        - Also, we need to implement the JupyterHub templates so that we can get the extra options
        - Attention!!! For those extra options, we need to check security!
    """

    profiles = List(
        trait = Tuple( Unicode(), Unicode(), Type(Spawner), Dict() ),
        default_value = [ ( 'Login Node Jupyter Server', 'local', LocalProcessSpawner,
                            {'start_timeout': 30, 'http_timeout': 25} ) ],
        minlen = 1,
        config = True,
        help = """List of profiles to offer for selection. Signature is:
            List(Tuple( Unicode, Unicode, Type(Spawner), Dict )) corresponding to
            1. display name (show in the selection menu)
            2. unique key (used to identify the profile)
            3. Spawner class (specify which spawner to use)
            4. Spawner config options (limit of the options, such as min, max of memory, hour, CPU cores)
            """
        )

    child_profile = Unicode()

    form_template = Unicode(
        """<label for="profile"><i class="fa fa-caret-square-o-down" aria-hidden="true"></i> If you need more time or resource, feel free to <a href="/contact/" target="_blank" rel="noopener noreferrer">contact ADMIN <i class="fa fa-user-secret" aria-hidden="true"></i></a></label>
        <br>
        <label for="profile"><i class="fa fa-caret-square-o-down" aria-hidden="true"></i> Select a job queue you like <i class="fa fa-hand-o-down" aria-hidden="true"></i></label>
        
        <select id="queue" class="form-control" name="profile" required autofocus>
        {input_template}
        </select>
        """,
        config = True,
        help = """Template to use to construct options_form text. {input_template} is replaced with
            the result of formatting input_template against each item in the profiles list."""
        )

    first_template = Unicode('selected',
        config=True,
        help="Text to substitute as {first} in input_template"
        )

    input_template = Unicode("""
        <option value="{key}" {first}>{display}</option>""",
        config = True,
        help = """Template to construct {input_template} in form_template. This text will be formatted
            against each item in the profiles list, in order, using the following key names:
            ( display, key, type ) for the first three items in the tuple, and additionally
            first = "checked" (taken from first_template) for the first item in the list, so that
            the first item starts selected."""
        )

    options_form = Unicode()

    def _options_form_default(self):
        temp_keys = [ dict(display=p[0], key=p[1], type=p[2], first='') for p in self.profiles ]
        temp_keys[0]['first'] = self.first_template
        text = ''.join([ self.input_template.format(**tk) for tk in temp_keys ])
        return self.form_template.format(input_template=text)

    def options_from_form(self, formdata):
        '''Here is how we get args from the front-end.
           In other words, we need get these extra args from jinja template!
             profile: type of profile, 
               e.g. str(local), str(small), str(fat)
             hours_xxx: how many hours do you need? (h)
               e.g. int(6)
             cpu_xxx: how many cores do you need? (core)
               e.g. int(72)
             memory_xxx: how much memory do you need? (G)
               e.g. int(100)
        '''
        # Default to first profile if somehow none is provided
        _data = dict(profile=formdata.get('profile', [self.profiles[0][1]])[0])
        # let's get extra args
        for key in ['hours_small', 'cpu_small', 'memory_small', 'hours_fat', 'cpu_fat', 'memory_fat']:
            _data[key] = formdata.get(key, "1")
        return _data

    # load/get/clear : save/restore child_profile (and on load, use it to update child class/config)

    def select_profile(self, profile):
        '''Considering security and limitation, let's check these args according to their limits!
        '''
        # Select matching profile, or do nothing (leaving previous or default config in place)
        for p in self.profiles:
            # local is LocalProcessSpawner
            if p[1] == 'local' == profile:
                self.child_class = p[2]
                self.child_config = p[3]
                return
            # small/fat/gpu is batchspawner
            elif p[1] == profile:
                if profile == 'fat':
                    _prefix = '_fat'
                elif profile == 'small' or profile == 'gpu':
                    _prefix = '_small'
                else:
                    return

                # get limit from jupyterhub_config.py
                min_hours, max_hours = p[3]['min_max_hour']
                min_cpu, max_cpu = p[3]['min_max_cpu']
                min_mem, max_mem = p[3]['min_max_memory']

                _hours = int(self.extra_args['hours'+_prefix])
                _cpu = int(self.extra_args['cpu'+_prefix])
                _mem = int(self.extra_args['memory'+_prefix])
                # check if the args value is in the expected range? if not, we set them as minimal
                if not (min_hours <= _hours <= max_hours) or not (min_cpu <= _cpu <= max_cpu) or not (min_mem <= _mem <= max_mem):
                    _hours, _cpu, _mem = min_hours, min_cpu, min_mem
                
                # set the final config, here is PBS script setting!
                self.child_class = p[2]  # what kind of spawner we will run?
                self.child_config['req_queue'] = str(profile)
                self.child_config['req_runtime'] = str(_hours)
                self.child_config['req_nprocs'] = str(_cpu)
                self.child_config['req_memory'] = str(_mem)
                return

    def construct_child(self):
        self.extra_args = dict()
        for key in ['hours_small', 'cpu_small', 'memory_small', 'hours_fat', 'cpu_fat', 'memory_fat']:
            self.extra_args[key] = self.user_options.get(key, [""])[0]
        # print("lalala")
        # print(self.extra_args)
        # print(self.user_options)
        self.child_profile = self.user_options.get('profile', "")
        self.select_profile(self.child_profile)
        super().construct_child()

    def load_child_class(self, state):
        try:
            self.child_profile = state['profile']
        except KeyError:
            self.child_profile = ''
        self.select_profile(self.child_profile)

    def get_state(self):
        state = super().get_state()
        state['profile'] = self.child_profile
        return state

    def clear_state(self):
        super().clear_state()
        self.child_profile = ''