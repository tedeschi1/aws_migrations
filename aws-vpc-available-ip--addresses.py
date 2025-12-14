###run "aws configure" to set the access key id and secret###

import boto3
import ipaddress
import sys

def find_available_subnets(vpc_id, subnet_prefix_length):
    """
    Finds available subnets of a given size within an AWS VPC.

    Args:
        vpc_id (str): The ID of the VPC to search.
        subnet_prefix_length (int): The CIDR prefix length for the desired subnets (e.g., 26 for /26).

    Returns:
        list: A list of available subnet CIDR blocks as strings.
    """
    try:
        # Initialize the EC2 client
        ec2 = boto3.client('ec2')

        # Get the VPC information to find its primary CIDR block
        print(f"Retrieving VPC information for {vpc_id}...")
        vpc_response = ec2.describe_vpcs(VpcIds=[vpc_id])
        if not vpc_response['Vpcs']:
            print(f"Error: VPC with ID '{vpc_id}' not found.")
            return []
        
        vpc_cidr_block = vpc_response['Vpcs'][0]['CidrBlock']
        print(f"Found VPC CIDR: {vpc_cidr_block}")

        # Get a list of all existing subnets in the VPC
        print("Retrieving existing subnets...")
        subnets_response = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        
        used_cidrs = [subnet['CidrBlock'] for subnet in subnets_response['Subnets']]
        
        # Convert used CIDRs to ipaddress.IPv4Network objects for easier comparison
        used_networks = set()
        for cidr in used_cidrs:
            try:
                used_networks.add(ipaddress.IPv4Network(cidr))
            except ValueError as e:
                print(f"Warning: Skipping invalid CIDR block '{cidr}': {e}")

        print(f"Found {len(used_networks)} existing subnets.")

        # Calculate all possible subnets of the desired size within the VPC's CIDR
        vpc_network = ipaddress.IPv4Network(vpc_cidr_block)
        
        if subnet_prefix_length < vpc_network.prefixlen:
            print(f"Error: The desired subnet prefix length ({subnet_prefix_length}) must be "
                  f"larger than the VPC prefix length ({vpc_network.prefixlen}).")
            return []

        all_possible_subnets = list(vpc_network.subnets(new_prefix=subnet_prefix_length))

        # Compare the lists to find the available subnets
        available_subnets = []
        for possible_subnet in all_possible_subnets:
            is_available = True
            for used_network in used_networks:
                # Check for overlap between the possible subnet and any used subnet
                if possible_subnet.overlaps(used_network):
                    is_available = False
                    break
            if is_available:
                available_subnets.append(str(possible_subnet))

        return available_subnets

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    # Example usage: Replace 'vpc-xxxxxxxxxxxxxxxxxx' with your VPC ID
    target_vpc_id = 'vpc-xxxxxxxxxxx'
    target_subnet_prefix = 27

    print(f"Scanning for available /{target_subnet_prefix} subnets in VPC ID: {target_vpc_id}\n")

    available_subnets = find_available_subnets(target_vpc_id, target_subnet_prefix)

    if available_subnets:
        print("\n--- Available Subnet CIDR Blocks ---")
        for subnet in available_subnets:
            print(subnet)
        print("------------------------------------")
        print(f"Total available /26 subnets found: {len(available_subnets)}")
    else:
        print("No available subnets found, or an error occurred.")
