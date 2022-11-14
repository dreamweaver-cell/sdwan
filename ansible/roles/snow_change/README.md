# snow_change

Role can:

1.  Create a new Change
2.  Create a related Change Task
3.  Cloose a ticket

Create a service-now change

- Create a service-now change
- Create a service-now task
- Send the change to approval
- Schedule change
- Set change to implement

Close a service-now change

- Move Change from implement to review
- Close task
- Close change

# time and dates

    - name: INCLUDE CHANGE VARIABLES
      ansible.builtin.include_vars: change_request_vars.yml
    - ansible.builtin.set_fact:
        sn_start_date: '{{lookup(''pipe'',''date -u +%Y-%m-%d" "%H:%M:00'')}}'
        sn_end_date: '{{lookup(''pipe'',''date -u -d "+1 hour" +%Y-%m-%d" "%H:%M:00'')}}'

# Requirements

Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required.

## Role Variables

Each varaible should include infromation regarding the change

## Dependencies

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

## Example Playbook

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

## License

BSD

## Author Information

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
