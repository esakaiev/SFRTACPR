# HOW TO Documentation

#1. Python package dependencies:
- sudo pip install pyping
- sudo pip install scp

#2. Configuration files
- Current scripts includes next cfg files to set information about the  testing systems:
2.1 - configuration/dependency.yml: includes packages, that required by ansible
    Example:

2.2 - configuration/fedorapeople_cfg: - includes 2 keys: fedorapeople and paths.
    - fedorapeople key store information about fedorapeople account, to create repo inside for providing PR.
    - paths key includes paths on the localhost, where repository should be created and then uploaded to fedorapeople.
       (some workarounnd for known issue of fedorapeople).

2.3 - configuration/input_packages.yml. Includes package under tests, that will be cloned from the repo, mentioned
       in paths.yml cfg file.
       - gdb: [classic, container, atomic]. This structure includes tags, that needs to be execute. If some tags
       do not lists, script will skip this execution.

2.4 configuration/openstack.yml: Includes information about servers, where tests will be executed.
    includes 2 mandatory keys: tags and openstack.
    - keys - dependency for what tags needs to be executed under openstack image.
    - openstack - list of servers, where need to run tests.

2.5 configuration/paths.yml - includes general information.
   UPSTREAM_GIT_PATH key - root of path to the upstreamfirst git, whole pack will be group with package name.



#3. Execution.

- Scripts include main.py python script, that will started execution of tests, it includes next steps:

 - prepare_environment
 - download_tests
 - execute_tests

#4. Prepare repository for PR on fedorapeople:
 - need to execute script fedorapeople/prepare_fedorapeople_repo.py, that will download tests from repo,
    mentioned in paths.yml and then create repo on fedorapeople for porting tests on pagure.


