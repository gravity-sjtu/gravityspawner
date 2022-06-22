# gravityspawner for Jupyterhub

This package is for [**Gravity of DOA, SJTU**](https://gravity.sjtu.edu.cn/)

We attend to select PBS/Slurm job queue first, then input arguments like *hours, memory, CPU cores* to spawn a Jupyter server.

We need to combine *templates* and *wrapspawner* to achieve this goal:
```shell
├── jupyterhub
│   └── templates               # jinja template
│       ├── page.html           # change the navigation bar, add some button
│       ├── spawn.html          # user can select and input arguments such as hour, cpu, memory. use JavaScript to hide the input form.
│       └── spawn_pending.html  # waiting for spawning server, add some message
└── src
    ├── gravityspawner
        ├── gravityspawner.py   # get extra arguments from jinja template, then pass them to batchspawner [thanks wrapspawner.ProfilesSpawner]. set resource limits as well.
```

## Installation

Install via **pip**:

   ```shell
   pip install gravityspawner
   ```
   Or, another better way to use **pip**:
   ```shell
   python -m pip install gravityspawner
   ```

## Usage
1. Add lines in `jupyterhub_config.py`:
   
   ```python
      c.JupyterHub.spawner_class = 'gravityspawner.GravitySpawner'
   ```

2. If we use `batchspawner.TorqueSpawner`, then add these lines in `jupyterhub_config.py`:

   ```python
   c.GravitySpawner.profiles = [
      ('[ LOGIN 01 ] 8 cores 8 GB running forever (unless idle for more than 3 days)', 'local', 'jupyterhub.   spawner.LocalProcessSpawner', {'ip':'0.0.0.0'} ),
      ('[ SMALL ] Max: [ 72 cores + 400 GB ]', 'small', 'batchspawner.TorqueSpawner',
         dict(min_max_hour=(1,12),min_max_cpu=(8,72),min_max_memory=(10,360))),
      ('[ GPU ] Max: [ 72 cores + 400 GB + NVIDIA Tesla V100 32GB ]', 'gpu', 'batchspawner.TorqueSpawner',
         dict(min_max_hour=(1,12),min_max_cpu=(8,72),min_max_memory=(10,360))),
      ('[ FAT ] Max: [ 192 cores + 6000 GB ]', 'fat', 'batchspawner.TorqueSpawner',
         dict(min_max_hour=(1,12),min_max_cpu=(8,192),min_max_memory=(400,6000))),
   ]
   ```
   **profiles** here represent *display, key, Spawner, options*. We can set limits of resource here, such as *hour, memory, CPU cores*. If you need more options or change options, you also need to edit the `jupyterhub/templates/spawn.html` (front-end)

The final *piece of* configuration of `jupyterhub_config.py` like this:
```python
import batchspawner
import gravityspawner

# our jinja template, change front-end style and add extra options
c.JupyterHub.template_paths = ['/opt/jupyterhub/templates']

# specify the spawner we use
c.JupyterHub.spawner_class = 'gravityspawner.GravitySpawner'

# PBS script to start Jupyter on computing nodes!
c.TorqueSpawner.batch_script = '''#!/bin/bash
#PBS -N jupyterhub
#PBS -q {queue}
#PBS -l walltime={runtime}:00:00
#PBS -l nodes=1:ppn={nprocs}
#PBS -l mem={memory}gb
####PBS -v {keepvars}
#PBS -V
#PBS -j oe
#PBS -o /home/$USER/.jupyter/jupyterhub.log
conda deactivate 1>/dev/null 2>&1
conda deactivate 1>/dev/null 2>&1
module load anaconda/conda-4.12.0 cuda/cuda-11.3
source /opt/conda/conda-4.12.0/bin/activate
conda activate /opt/jupyterhub/envs/hub02
{cmd}
'''

# Defaul options of Spawner. local + small + gpu + fat
c.GravitySpawner.profiles = [
   ('[ LOGIN 02 ] 8 cores 8 GB running forever (unless idle for more than 3 days)', 'local', 'jupyterhub.spawner.LocalProcessSpawner', {'ip':'0.0.0.0'} ),
   ('[ SMALL ] Max: [ 72 cores + 400 GB ]', 'small', 'batchspawner.TorqueSpawner',
      dict(min_max_hour=(1,12),min_max_cpu=(8,72),min_max_memory=(10,360))),
   ('[ GPU ] Max: [ 72 cores + 400 GB + NVIDIA Tesla V100 32GB ]', 'gpu', 'batchspawner.TorqueSpawner',
      dict(min_max_hour=(1,12),min_max_cpu=(8,72),min_max_memory=(10,360))),
   ('[ FAT ] Max: [ 192 cores + 6000 GB ]', 'fat', 'batchspawner.TorqueSpawner',
      dict(min_max_hour=(1,12),min_max_cpu=(8,192),min_max_memory=(400,6000))),
]
```

## Example

This is a typical dropdown menu letting the user choose between local **Login node** and **Torque/PBS queues**
![selection menu](https://github.com/lalalabox/gravityspawner/raw/master/imgs/select.png)

After using `jupyterhub/templates`, we can input args according to our selection, e.g.🌰
1. select **login node**, which is `'local'` in code:
![select login node](https://github.com/lalalabox/gravityspawner/raw/master/imgs/input_local.png)
2. select **Torque/PBS gpu queue**, which is `'gpu'` in code:
![select PBS gpu queue](https://github.com/lalalabox/gravityspawner/raw/master/imgs/input_gpu.png)

