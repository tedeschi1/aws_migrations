
import boto3
from tabulate import tabulate

def get_vpc_resources(vpc_id, region='us-east-1'):
    ec2 = boto3.client('ec2', region_name=region)
    report = {}

    # EC2 Instances
    instances = ec2.describe_instances(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    report['EC2 Instances'] = [
        {
            'InstanceId': i['InstanceId'],
            'State': i['State']['Name'],
            'PrivateIp': i.get('PrivateIpAddress'),
            'PublicIp': i.get('PublicIpAddress'),
            'Tags': ', '.join([f"{tag['Key']}={tag['Value']}" for tag in i.get('Tags', [])])
        }
        for r in instances['Reservations'] for i in r['Instances']
    ]

    # Subnets
    subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    report['Subnets'] = [
        {
            'SubnetId': s['SubnetId'],
            'CidrBlock': s['CidrBlock'],
            'AvailabilityZone': s['AvailabilityZone']
        }
        for s in subnets['Subnets']
    ]

    # Route Tables
    route_tables = ec2.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    report['Route Tables'] = [
        {
            'RouteTableId': rt['RouteTableId'],
            'Routes': ', '.join([
                r.get('DestinationCidrBlock', 'N/A') + ' → ' + r.get('GatewayId', 'N/A')
                for r in rt['Routes']
            ])
        }
        for rt in route_tables['RouteTables']
    ]

    # Security Groups
    security_groups = ec2.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    report['Security Groups'] = [
        {
            'GroupId': sg['GroupId'],
            'GroupName': sg['GroupName'],
            'Description': sg['Description']
        }
        for sg in security_groups['SecurityGroups']
    ]

    # Network Interfaces
    interfaces = ec2.describe_network_interfaces(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    report['Network Interfaces'] = [
        {
            'InterfaceId': ni['NetworkInterfaceId'],
            'PrivateIp': ni['PrivateIpAddress'],
            'Status': ni['Status']
        }
        for ni in interfaces['NetworkInterfaces']
    ]

    return report

def print_report(report):
    for category, items in report.items():
        print(f"\n=== {category} ===")
        if items:
            print(tabulate(items, headers="keys", tablefmt="grid"))
        else:
            print("No resources found.")

# Example usage
if __name__ == "__main__":
    vpc_id = 'vpc-04a0282ac790cafdf'  # Replace with your VPC ID
    region = 'us-east-1'     # Replace with your AWS region
    resources = get_vpc_resources(vpc_id, region)
    print_report(resources)
