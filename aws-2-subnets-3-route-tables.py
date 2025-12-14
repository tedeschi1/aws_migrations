# This script creates two subnets and three route tables within an existing AWS VPC.
# One subnet for each of the Aviatrix gateways 
# Two route tables to be used for workload subnets in the VPC so traffic can be routed to each of the Aviatrix gw's
# One route table for the Aviatrix gateway subnets

import boto3
from botocore.exceptions import ClientError

def create_vpc_resources(vpc_id, subnet_az_1, subnet_az_2, subnet_cidr_1, subnet_cidr_2):
    """
    Creates two subnets and three route tables in a specified VPC.

    Args:
        vpc_id (str): The ID of the existing VPC.
        subnet_az_1 (str): The Availability Zone for the first subnet.
        subnet_az_2 (str): The Availability Zone for the second subnet.
        subnet_cidr_1 (str): The CIDR block for the first subnet (e.g., '10.0.1.0/24').
        subnet_cidr_2 (str): The CIDR block for the second subnet (e.g., '10.0.2.0/24').
    """
    # Initialize the EC2 client
    ec2 = boto3.client('ec2')

    try:
        # Create Subnets
        print("Creating subnets...")
        
        # Subnet 1
        subnet1_response = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=subnet_cidr_1,
            AvailabilityZone=subnet_az_1
        )
        subnet1_id = subnet1_response['Subnet']['SubnetId']
        print(f"Successfully created subnet: {subnet1_id} in {subnet_az_1}")

        # Subnet 2
        subnet2_response = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=subnet_cidr_2,
            AvailabilityZone=subnet_az_2
        )
        subnet2_id = subnet2_response['Subnet']['SubnetId']
        print(f"Successfully created subnet: {subnet2_id} in {subnet_az_2}")
        
        # Create Route Tables
        print("\nCreating route tables...")

        route_tables = []
        for i in range(1, 4):
            rt_response = ec2.create_route_table(VpcId=vpc_id)
            rt_id = rt_response['RouteTable']['RouteTableId']
            route_tables.append(rt_id)
            print(f"Successfully created route table {i}: {rt_id}")

    except ClientError as e:
        print(f"An error occurred: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

    return True

# --- Main script execution ---
if __name__ == "__main__":
    # --- USER VARIABLES TO BE SET ---
    # Replace with your existing VPC ID
    VPC_ID = 'vpc-xxxxxxxx'

    # Specify the Availability Zones for the new subnets
    SUBNET_AZ_1 = 'us-east-1a'
    SUBNET_AZ_2 = 'us-east-1b'
    
    # Specify the CIDR blocks for the new subnets
    SUBNET_CIDR_1 = '10.200.0.128/27'
    SUBNET_CIDR_2 = '10.200.0.160/27'

    # Check if variables are set
    if not all([VPC_ID, SUBNET_AZ_1, SUBNET_AZ_2, SUBNET_CIDR_1, SUBNET_CIDR_2]):
        print("Please set all variables in the script before running.")
    else:
        print(f"Attempting to create resources in VPC: {VPC_ID}")
        success = create_vpc_resources(VPC_ID, SUBNET_AZ_1, SUBNET_AZ_2, SUBNET_CIDR_1, SUBNET_CIDR_2)
        if success:
            print("\nScript completed successfully.")
        else:
            print("\nScript failed to complete.")
