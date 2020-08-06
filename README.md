# Watson-Ansible-Assistant

Watson Ansible Assistant (W2A) is a tool that allows you to run playbooks and interact with Ansible from a virtual assistant (chatbot) using "natural language" (without technical commands) in some messaging system such as Slack (only Slack available in this version).

With this version of W2A you can perform the following activities in Ansible, without using commands. Only with natural language through a chatbot:

- Validate the syntax in the code of the playbooks.
- Run mock executions of the playbooks.
- Run the playbooks.

### The way W2A operates:
![Slack --> W2A(Ansible) --> IBM Watson Assistant --> W2A(Ansible) --> Slack ](https://github.ibm.com/Anderson-Jose-Campos-Rosales/Watson-Ansible-Assistant/blob/master/_img/w2a_diagram.png?raw=true)

### Simple example of use:
![Sample 1: Check sintax of playbooks from Slack](https://github.ibm.com/Anderson-Jose-Campos-Rosales/Watson-Ansible-Assistant/blob/master/_img/Sample1.png)

![Sample 2: Test of playbooks from Slack](https://github.ibm.com/Anderson-Jose-Campos-Rosales/Watson-Ansible-Assistant/blob/master/_img/Sample2.png)

![Sample 3: Run playbooks from Slack](https://github.ibm.com/Anderson-Jose-Campos-Rosales/Watson-Ansible-Assistant/blob/master/_img/Sample3.png)


## Get started using:

### IBM Watson Assistant configuration:
- Create one assistant in IBM Watson Assistant of your workspace in IBM Cloud.
  - More info: https://cloud.ibm.com/docs/services/assistant?topic=assistant-assistant-add
- Create a dialog skill for your assistant and <b>import the skills dialog in JSON format file, found in the "./w2a_resource" folder of this repository</b> (only available in English and Spanish)
  - More info: https://cloud.ibm.com/docs/services/assistant?topic=assistant-skill-add
- Add the dialog skill created to the assistant.


### Slack configuration:
The configuration of a bot in slack is simplified with the following gif:
![Slack bot creation](https://github.ibm.com/Anderson-Jose-Campos-Rosales/Watson-Ansible-Assistant/blob/master/_img/AppSlackCreation.gif)

Note: Set the scope minimal of your app slack in "Tools" menu, "Update to Granular scopes".

### Watson Ansible Assistant configuration:

  - <b>( i ) Requirements</b>:
      - Ansible
      - python 3.6 (It's assumed that you must have it installed, since ansible works with python)
        
      - Authentication based on SSH rsa keys to managed hosts to be able to authenticate without needing use a password. This         authentication method is also usually more secure and widely used today. (The user with whom this configuration is           made must be the one running w2a).
        If your rsa key uses a passphrase, you must use ssh-agent to store the password of the private key, so you can Run the playbooks via ssh quickly.
        
        
  - <b>Setting</b>:
      - Download or clone this repository.
      - Configure the parameters in the <b>w2a.cfg</b> file:
        - For connection with Watson:
            - Set Assistant ID in the ASSISTANT_ID parameter
            - Set the Api key of the assistant to the IAM_AUTHENTICATOR parameter.
            - Set your Workspace id to the WORKSPACE_ID parameter.
            
            ```
            [WATSON]
            ASSISTANT_ID = 22e146ca-d76e-7e7b-8ae4-8c4deb7e38c9
            # Api Key:
            IAM_AUTHENTICATOR = df6gSnkGqkGXNR7DP15nTbfSnQjVpdS1jJXrviZfRQBj
            SERVICE_URL = https://gateway.watsonplatform.net/assistant/api
            WORKSPACE_ID = 34086fe7-a9f8-49d8-e0a4-c0eb77235426
            ```

        - For connection with your slack application:
            - Set the Token of your application to the TOKEN parameter.
            
            ```
            [SLACK]
            TOKEN = xoxb-965960142123-847264569931-Wo56Cv6UK1yi8FOJaRx4dEGE
            ```
            
        - For interaction with Ansible:
            - Set Configure the directory where the playbooks with which w2a can work in the PLAYBOOKS_DIR parameter are located.
            By default the "./ansible_playbooks" directory of this directory is configured, you can replace it with another one if you wish.
            If you want to add more directories, you can do so by adding the parameters PLAYBOOKS_DIR1, PLAYBOOKS_DIR2, PLAYBOOKS_DIR3, etc ...

            - Configure the file path with the vaul password to run playbooks with confidential data, in the VAULT_PASS_FILE parameter.
            Of course, the user running w2a.py must have permission to read that file.

           ```
           [ANSIBLE]
           PLAYBOOKS_DIR = ./ansible_playbooks
           VAULT_PASS_FILE = ./ansible_vault/vault-pass
           ```


        - For W2A configuration:
            - Set the path of the w2a log in the FILE_LOG parameter, by default it is "./logs". 
            
            ```
            [W2A]
            FILE_LOG = ./logs/w2a.log
            ```
            
            
      - For the operation of w2a.py, install the required modules with the commands:<br>
            - ```pip3 install --upgrade "ibm-watson>=4.1.0"``` <br>
            - ```pip3 install slackclient```
            
  - <b>Execution</b>.
      - To start working with Watson Ansible Assistant, run the <b>w2a.py</b> file once all previous configuration is finished:

          - ```python3 w2a.py```

      - Add your bot application to your Slack workspaces and start interacting with this. ;-)
        
          
