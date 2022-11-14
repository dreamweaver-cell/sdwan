# SNAP

SDWAN Network Automation Platform

This is a collection of scripts used for gathering information from the network and provision sdwan routers.

## Set up the development environment

These instructions in for setting up an dev environment using a devcontainer on the internal server srv10432.

Prerequisites:

- Make sure you can connect to srv10432 with your nofh-account with ssh-key.
- Your nofh-account need to be in "docker" group in srv10432
- Configure git on srv10432 eg:
  ```
  git config --global user.name "Jacob Garder"
  git config --global user.email "jacob.garder@hm.com"
  ```

1. Install VS Code extension: remote - SSH : [install instructions](https://code.visualstudio.com/docs/remote/ssh-tutorial).  
   As remote-host, use srv10432.hm.com and use your nofh-account as username.
2. Command palette, `Remote ssh: Connect to host -> new host` and put in `ssh nofhxxxxx@srv10432.hm.com -A` (use your nofh-account )
3. Connect to the ssh-host from VS Code (click on the green box in the left lower corner in VSC)
4. From command palette, `git: clone` and put in this repo (`https://github.com/hm-group/sdwan.git`)
5. Cancel when asked to repoen in container
6. Copy the file .devcontainer/devcontainer.env.template to .devcontainer/devcontainer.env and update the variables with information provided from global-connectivity
7. Either clone the repo [snapconfig](https://github.com/hm-group/snapconfig) or just create an empty sub-directory called snapconfig
8. Close VSCode
9. Reopen VSCode, connect to remote host and open the directory.
10. Click the button "Reopen in container" when asked. Wait a couple of seconds for the container to build and configure.

Now the environment is up and running

## Contribute

1. Make sure the code passes the linting-tests and pytest.
2. Publish a new branch with appropriate name
3. Make a pull request to merge into main-branch
