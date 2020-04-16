# This script sample is part of "Learn Azure in a Month of Lunches - 2nd edition" (Manning
# Publications) by Iain Foulds.
#
# This sample script covers the exercises from chapter 4 of the book. For more
# information and context to these commands, read a sample of the book and
# purchase at https://www.manning.com/books/learn-azure-in-a-month-of-lunches-second-edition
#
# This script sample is released under the MIT license. For more information,
# see https://github.com/fouldsy/azure-mol-samples-2nd-ed/blob/master/LICENSE

import string,random,time,azurerm,json,subprocess,platform
from azure.storage.queue import QueueService

try:
    # Define variables to handle Azure authentication
    if platform.system() == "Linux":
        get_token = subprocess.run(['az account get-access-token | jq  -r .accessToken'], stdout=subprocess.PIPE, shell=True)
    else:
        get_token = subprocess.run(['.\getaccesstoken.bat'], stdout=subprocess.PIPE, shell=True)

    auth_token = get_token.stdout.decode('utf8').rstrip()
    subscription_id = azurerm.get_subscription_from_cli()

    # Define variables with random resource group and storage account names
    resourcegroup_name = 'azuremol'+''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    storageaccount_name = 'azuremol'+''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    location = 'westeurope'

    ###
    # Create the a resource group for our demo
    # We need a resource group and a storage account. A random name is generated, as each storage account name must be globally unique.
    ###
    response = azurerm.create_resource_group(auth_token, subscription_id, resourcegroup_name, location)
    if response.status_code == 200 or response.status_code == 201:
        print(('Resource group: ' + resourcegroup_name + ' created successfully.'))
    else:
        print('Error creating resource group')

    # Create a storage account for our demo
    response = azurerm.create_storage_account(auth_token, subscription_id, resourcegroup_name, storageaccount_name,  location, storage_type='Standard_LRS')
    if response.status_code == 202:
        print(('Storage account: ' + storageaccount_name + ' created successfully.'))
        print('\nWaiting for storage account to be ready before we create a Queue')
        time.sleep(30)
    else:
        print('Error creating storage account')


    ###
    # Use the Azure Storage Storage SDK for Python to create a Queue
    ###
    print('\nLet\'s create an Azure Storage Queue to drop some messages on.')
    input('Press Enter to continue...')

    # Each storage account has a primary and secondary access key.
    # These keys are used by aplications to access data in your storage account, such as Queues.
    # Obtain the primary storage access key for use with the rest of the demo

    response = azurerm.get_storage_account_keys(auth_token, subscription_id, resourcegroup_name, storageaccount_name)
    storageaccount_keys = json.loads(response.text)
    storageaccount_primarykey = storageaccount_keys['keys'][0]['value']

    # Create the Queue with the Azure Storage SDK and the access key obtained in the previous step
    queue_service = QueueService(account_name=storageaccount_name, account_key=storageaccount_primarykey)
    response = queue_service.create_queue('taskqueue')
    if response == True:
        print('Storage Queue: taskqueue created successfully.\n')
    else:
        print('Error creating Storage Queue.\n')
    ########################################################################################## START ACTION
    queue_service = QueueService(account_name=storageaccount_name, account_key=storageaccount_primarykey)
    # create queue

    input('Queue created, Press Enter to continue...')

    # setup queue Base64 encoding and decoding functions (if binary queue messages are required)
    #queue_service.encode_function = QueueMessageFormat.binary_base64encode
    #queue_service.decode_function = QueueMessageFormat.binary_base64decode

    # fill queue
    queue_service.put_message('taskqueue', u'Hello World001')
    queue_service.put_message('taskqueue', u'Hello World002')
    queue_service.put_message('taskqueue', u'Hello World003')
    
    input('Queue filled, Press Enter to continue...')
    metadata = queue_service.get_queue_metadata('taskqueue')
    nummsg = metadata.approximate_message_count
    print(('Number of messages in the queue: ' + str(nummsg)))
    # get a view of the queued messages
    messages = queue_service.peek_messages('taskqueue', num_messages=nummsg)
    for message in messages:
        print(message.content)
    
    input('Get messages, Press Enter to continue...')

    messages = queue_service.get_messages('taskqueue')
    # batch of 16 messages from queue, extended timeout
    #messages = queue_service.get_messages('taskqueue', num_messages=16, visibility_timeout=5*60)

    # update message content
    #for message in messages:
    #    queue_service.update_message('taskqueue', message.id, message.pop_receipt, 0, u'Hello World Again')

    for message in messages:
        print(message.content)
        queue_service.delete_message('taskqueue', message.id, message.pop_receipt)
    
    messages = queue_service.get_messages('taskqueue')


    ########################################################################################## STOP ACTION
    ###
    # This was a quick demo to see Queues in action.
    # Although the actual cost is minimal since we deleted all the messages from the Queue, it's good to clean up resources when you're done
    ###
    print('\nThis is a basic example of how Azure Storage Queues behave.\nTo keep things tidy, let\'s clean up the Azure Storage resources we created.')
    input('Press Enter to continue...')

    response = queue_service.delete_queue('taskqueue')
    if response == True:
        print('Storage Queue: taskqueue deleted successfully.')
    else:
        print('Error deleting Storage Queue')

    response = azurerm.delete_resource_group(auth_token, subscription_id, resourcegroup_name)
    if response.status_code == 202:
        print(('Resource group: ' + resourcegroup_name + ' deleted successfully.'))
    else:
        print('Error deleting resource group.')

except Exception as ex:
    print('Exception: ' + str(ex))
    





