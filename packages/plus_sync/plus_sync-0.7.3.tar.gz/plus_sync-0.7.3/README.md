# PLUS Sync

## What is this?
`plus_sync` is a command line tool to make it easier to synchronize data. It was built with a HPC, more specifically the SCC at the PLUS, setup in mind.

The idea is that you have an analysis project that needs data from one or more storages that cannot be mounted to work. `plus_sync` lets you
define the storage using a variety of options and synchronize them for you.

## Global Installation
If you don't use environments (venv, conda/mamba, pixi), you can also install `plus_sync` as a user.

The easiest way is to use the global `pixi` installation:

```bash
pixi global install plus_sync
```

Updating is as simple as:

```bash
pixi global upgrade-all
```

Alternatively, you can use `pip`:

```bash
pip install --user plus_sync
```

If this results in an error, your default python version might be too old. In this case, please try:

```bash
pip3.9 install --user plus_sync
```

## Installation
`plus_sync` can be installed from `pypi` and `conda-forge`. If you want to use it in your python environment, you can simply install it using the specific way of your environment:

### pip
Add `plus_sync` to your `requirements.txt` or install it directly using `pip install plus_sync`.

### conda
Add `plus_sync` as a dependency to your `environment.yml`

### pixi
```bash
pixi add plus_sync
```

## How to use it
`plus_sync` comes with extensive help. Just issue `plus_sync` and you are going to see all the commands and options.

`plus_sync` relies on a configuration file called `plus_sync.toml` to know where to look for your data. Fortunately, you do hardly need to interact with that file directly
as it offers some nice commands to create one and configure everything you need.

### Initialize
You can create a new configuration file by issueing

```bash
plus_sync init
```

It is going to ask you for the name of the project and then generate a `plus_sync.toml` file for you with some defaults.

### Add a remote

Use the `add` command to add remotes to the configuration. To get a list of possible remote types, type `plus_sync add`:

```bash
❯ plus_sync add
                                                                                                  
 Usage: plus_sync add [OPTIONS] COMMAND [ARGS]...                                                 
                                                                                                  
 Add new synchronisation items.                                                                   
                                                                                                  
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────╮
│ gitlab   Add a remote for a gitlab hosted project.                                             │
│ rclone   Add a RClone remote.                                                                  │
│ sftp     Add a SFTP remote.                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Just by appending one of the types, you can see a description on how to add a remote.

For instance, if your remote can be reached via sftp, you would do first see, how the command works:

```
❯ plus_sync add sftp
                                                                                                  
 Usage: plus_sync add sftp [OPTIONS] NAME HOST USER REMOTE_FOLDER                                 
                                                                                                  
 Add a SFTP remote.                                                                               
 In order to do passwordless login, you need to setup a ssh key pair and add the                  
 configuration to your ~/.ssh/config file.                                                        
                                                                                                  
 If no ssh configuration is present, you need to enter the password every time                    
 you use the remote.                                                                              
                                                                                                  
╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────╮
│ *    name               TEXT  The name of this remote [default: None] [required]               │
│ *    host               TEXT  The host of the SFTP server. [default: None] [required]          │
│ *    user               TEXT  The user to use for the SFTP server. [default: None] [required]  │
│ *    remote_folder      TEXT  The remote folder to use. (e.g.                                  │
│                               /mnt/sinuhe/data_raw/project_name)                               │
│                               [default: None]                                                  │
│                               [required]                                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────╮
│ --globs        TEXT     The pattern used to match the files. Can be used multiple times.       │
│                         [default: *.mat, *.fif]                                                │
│ --port         INTEGER  The port of the SFTP server. [default: 22]                             │
│ --help                  Show this message and exit.                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────╯
```

So, we know that we need to supply:

* The name of the remote. We can choose any name we want
* The hostname of the server we need to connect to
* The username you use to log in there
* The folder where the data is stored
* Additionally, the `--globs` options allows us to specifiy, what files to search for on the remote.

So, this is the command we need to use:

```bash
plus_sync add sftp my_sftp_remote my_storage_gateway.exampleuni.at gthreepwood /mnt/big_whoop
```

### Work with the remotes
Now you can use the following commands:

1. `plus_sync list-remotes`: Lists all configured remotes
2. `plus_sync ls my_sftp_remote`: Lists all files in the remote that would be synced
3. `plus_sync list-subjects my_sftp_remote`: List all the subjects that are found
4. `plus_sync sync my_sftp_remote`: Sync the data

### Why do my subject ids look funny?
This is a feature, not a bug. Some subject ids are generated in a way that anonymization is not perfect, because:

1. The ID might contain a birthdate or similar
2. The same ID is used in multiple experiments

In both cases, you do not want the original ID to be mentioned in a git repository that then ends up on gitlab/github, even in a private repository.

This is why `plus_sync` hashes the subject ids by default using the project name as a salt. This ensures that the same original subject id always results in the same hashed id within the same project but is completely unrecognisable and different between projects.


