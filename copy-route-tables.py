
import boto3

def copy_routes(source_route_table_id, destination_route_table_id, region='us-east-1'):
    ec2 = boto3.client('ec2', region_name=region)

    # Get routes from the source route table
    source_table = ec2.describe_route_tables(RouteTableIds=[source_route_table_id])['RouteTables'][0]
    routes = source_table['Routes']

    for route in routes:
        # Skip local route (cannot be created manually)
        if route.get('GatewayId') == 'local':
            continue

        # Prepare route parameters
        route_params = {
            'RouteTableId': destination_route_table_id
        }

        # Copy destination
        if 'DestinationCidrBlock' in route:
            route_params['DestinationCidrBlock'] = route['DestinationCidrBlock']
        elif 'DestinationIpv6CidrBlock' in route:
            route_params['DestinationIpv6CidrBlock'] = route['DestinationIpv6CidrBlock']
        elif 'DestinationPrefixListId' in route:
            route_params['DestinationPrefixListId'] = route['DestinationPrefixListId']

        # Copy target
        for key in ['GatewayId', 'InstanceId', 'NatGatewayId', 'TransitGatewayId', 'VpcPeeringConnectionId', 'NetworkInterfaceId', 'EgressOnlyInternetGatewayId', 'CarrierGatewayId', 'LocalGatewayId']:
            if key in route:
                route_params[key] = route[key]
                break
        try:
            ec2.create_route(**route_params)
            print(f"Copied route: {route_params}")
        except Exception as e:
            print(f"Failed to copy route: {route_params} — {e}")

# Example usage src_rt, dst_rt
copy_routes('rtb-xxxxxxxxxx', 'rtb-xxxxxxxxxxx', region='us-east-1')
