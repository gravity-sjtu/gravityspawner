# gravityspawner for Jupyterhub

This package is for [**Gravity of DOA, SJTU**](https://gravity.sjtu.edu.cn/)
- `jupyterhub/templates` is *jinja* template, where we add some extra options!
  - `jupyterhub/templates/spawn.html`: add **extra options**, such as `hour, cpu, memory`, so that you can set them totally free. Meanwhile, use JS to make the **input form appear/disappear**
  - `jupyterhub/templates/page.html`: change the navigation bar, including buttons and icons
  - `jupyterhub/templates/spawn_pending.html`: add some message
- `gravityspawner.py` is changed from [*wrapspawner.ProfilesSpawner*](https://github.com/jupyterhub/wrapspawner/blob/master/wrapspawner/wrapspawner.py#L165)
  - get extra options from the front-end, such as `hour, cpu, memory`
  - add some message when select **Server Option**
  - set the default limit of **Torque/PBS job**, which are `hour, cpu, memory` for different queue

## Installation

1. Install via **pip**:

   ```shell
   pip install gravityspawner
   ```
   Or, another better way to use **pip**:
   ```shell
   python -m pip install gravityspawner
   ```

2. Add lines in `jupyterhub_config.py`:
   
   ```python
      c.JupyterHub.spawner_class = 'gravityspawner.GravitySpawner'
   ```

3. If we use `batchspawner.TorqueSpawner`, then add these lines to `jupyterhub_config.py`:

   ```python
   c.GravitySpawner.profiles = [
      ('[ LOGIN 01 ] 8 cores 8 GB running forever (unless   idle for more than 3 days)', 'local', 'jupyterhub.   spawner.LocalProcessSpawner', {'ip':'0.0.0.0'} ),
      ('[ SMALL ] Max: [ 72 cores + 400 GB ]', 'small',  'batchspawner.TorqueSpawner',
         dict(req_nprocs='24', req_queue='small',  req_runtime='9:00:00', req_memory='120gb')),
      ('[ GPU ] Max: [ 72 cores + 400 GB + NVIDIA Tesla V100   32GB ]', 'gpu', 'batchspawner.TorqueSpawner',
         dict(req_nprocs='72', req_queue='gpu',    req_runtime='6:00:00', req_memory='360gb')),
      ('[ FAT ] Max: [ 192 cores + 6000 GB ]', 'fat',    'batchspawner.TorqueSpawner',
         dict(req_nprocs='60', req_queue='fat',    req_runtime='3:00:00', req_memory='1800gb')),
   ]
   ```
   Actually, `dict(xxx='xxx',...,'xxx'='xxx')` is **useless** here, cause we've already let these arguments set by **user input** in front-end, so the `dict` here won't make any effect at all, but we just keep it here for ~~format beauty (✿◡‿◡)~~

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
module load anaconda/conda-4.12.0 && source activate
conda activate /opt/jupyterhub/envs/hub01
{cmd}
'''

# Defaul options of Spawner. local + small + gpu + fat
c.GravitySpawner.profiles = [
   ('[ LOGIN 01 ] 8 cores 8 GB running forever (unless idle for more than 3 days)', 'local', 'jupyterhub.spawner.LocalProcessSpawner', {'ip':'0.0.0.0'} ),
   ('[ SMALL ] Max: [ 72 cores + 400 GB ]', 'small', 'batchspawner.TorqueSpawner',
      dict(req_nprocs='24', req_queue='small', req_runtime='9:00:00', req_memory='120gb')),
   ('[ GPU ] Max: [ 72 cores + 400 GB + NVIDIA Tesla V100 32GB ]', 'gpu', 'batchspawner.TorqueSpawner',
      dict(req_nprocs='72', req_queue='gpu', req_runtime='6:00:00', req_memory='360gb')),
   ('[ FAT ] Max: [ 192 cores + 6000 GB ]', 'fat', 'batchspawner.TorqueSpawner',
      dict(req_nprocs='60', req_queue='fat', req_runtime='3:00:00', req_memory='1800gb')),
]
```

### Example

This is a typical dropdown menu letting the user choose between local **Login node** and **Torque/PBS queues**
![selection menu](imgs/select.png)

After using `jupyterhub/templates`, we can input args according to our selection, e.g.🌰
1. select **login node**, which is `'local'` in code:
![select login node](imgs/input_local.png)
2. select **Torque/PBS gpu queue**, which is `'gpu'` in code:
![select PBS gpu queue](imgs/input_gpu.png)

