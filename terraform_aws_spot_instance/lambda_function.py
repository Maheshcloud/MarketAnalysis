import boto3
import os
import json

ec2 = boto3.client('ec2')

def start_instance():
    ami_id = os.environ.get('AMI_ID')
    instance_type = os.environ.get('INSTANCE_TYPE')
    key_name = os.environ.get('KEY_NAME')
    security_group_ids = os.environ.get('SECURITY_GROUP_IDS').split(',')
    spot_price = os.environ.get('SPOT_PRICE')
    instance_tag_key = os.environ.get('INSTANCE_TAG_KEY')
    instance_tag_value = os.environ.get('INSTANCE_TAG_VALUE')
    eip_allocation_id = os.environ.get('EIP_ALLOCATION_ID')

    print(f"Attempting to start instance with AMI: {ami_id}, Type: {instance_type}, Key: {key_name}, SG: {security_group_ids}, Spot Price: {spot_price}")

    try:
        response = ec2.request_spot_instances(
            InstanceCount=1,
            LaunchSpecification={
                'ImageId': ami_id,
                'InstanceType': instance_type,
                'KeyName': key_name,
                'SecurityGroupIds': security_group_ids,
                'Placement': {
                    'AvailabilityZone': f'{os.environ.get("AWS_REGION")}a' # Example AZ, consider making this dynamic or configurable
                },
                'TagSpecifications': [
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'MarketAnalysisSpotInstance'
                            },
                            {
                                'Key': instance_tag_key,
                                'Value': instance_tag_value
                            },
                        ]
                    },
                ]
            },
            SpotPrice=spot_price,
            Type='one-time'
        )
        print(f"Spot instance request successful: {json.dumps(response, indent=2)}")

        # Wait for the instance to be running and then associate EIP
        spot_instance_request_id = response['SpotInstanceRequests'][0]['SpotInstanceRequestId']
        waiter = ec2.get_waiter('spot_instance_request_fulfilled')
        waiter.wait(SpotInstanceRequestIds=[spot_instance_request_id])

        # Get the instance ID from the fulfilled request
        fulfilled_request = ec2.describe_spot_instance_requests(
            SpotInstanceRequestIds=[spot_instance_request_id]
        )['SpotInstanceRequests'][0]
        instance_id = fulfilled_request['InstanceId']

        print(f"Spot instance {instance_id} is running. Associating EIP {eip_allocation_id}...")
        ec2.associate_address(
            InstanceId=instance_id,
            AllocationId=eip_allocation_id
        )
        print(f"EIP {eip_allocation_id} associated with instance {instance_id}.")

    except Exception as e:
        print(f"Error starting instance or associating EIP: {e}")
        raise

def terminate_instance():
    instance_tag_key = os.environ.get('INSTANCE_TAG_KEY')
    instance_tag_value = os.environ.get('INSTANCE_TAG_VALUE')

    print(f"Attempting to terminate instances with tag {instance_tag_key}={instance_tag_value}")

    try:
        response = ec2.describe_instances(
            Filters=[
                {
                    'Name': f'tag:{instance_tag_key}',
                    'Values': [instance_tag_value]
                },
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                },
            ]
        )

        instance_ids = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])

        if instance_ids:
            print(f"Found instances to terminate: {instance_ids}")
            # Disassociate EIP before terminating if it's associated
            for instance_id in instance_ids:
                try:
                    addresses = ec2.describe_addresses(Filters=[{'Name': 'instance-id', 'Values': [instance_id]}])['Addresses']
                    for address in addresses:
                        if 'AssociationId' in address:
                            print(f"Disassociating EIP {address['AllocationId']} from {instance_id}")
                            ec2.disassociate_address(AssociationId=address['AssociationId'])
                except Exception as e:
                    print(f"Could not disassociate EIP from {instance_id}: {e}")

            ec2.terminate_instances(InstanceIds=instance_ids)
            print("Instances terminated successfully.")
        else:
            print("No running instances found with the specified tag.")

    except Exception as e:
        print(f"Error terminating instance: {e}")
        raise

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event, indent=2)}")

    if 'action' in event:
        action = event['action']
        if action == 'start':
            start_instance()
        elif action == 'terminate':
            terminate_instance()
        else:
            print(f"Unknown action: {action}")
            raise ValueError(f"Unknown action: {action}")
    else:
        print("No 'action' specified in the event. Defaulting to terminate for safety.")
        # For safety, if no action is specified, assume terminate or raise an error
        # For this example, we'll raise an error to force explicit action.
        raise ValueError("No 'action' specified in the event. Please specify 'start' or 'terminate'.")