# -*- coding: utf-8 -*-
from troposphere import Join, Output
from troposphere import Parameter, Ref, Tags
import troposphere.ec2 as ec2
from base import CloudformationAbstractBaseClass


class Vpc(CloudformationAbstractBaseClass):

    def __init__(self, sceptre_user_data):
        super(self.__class__, self).__init__()
        self.template.add_description("""Wordpress VPC""")

        self.add_parameters()
        self.add_resource()
        self.add_outputs()

    def add_parameters(self):
        t = self.template

        VALID_CIDR_IP_REGEX = (
            "\\d{1,3}+\\.\\d{1,3}+\\.\\d{1,3}+\\.\\d{1,3}/(\\d{1,2})")
        INVALID_CIDR_IP_MSG = "Must be a valid CIDR IP address xx.xx.xx.xx/xx"

        self.VpcCidr = t.add_parameter(Parameter(
            "VpcCidr",
            Default="10.0.0.0/16",
            Type="String",
            Description="CIDR address for the VPC to be created.",
            AllowedPattern=VALID_CIDR_IP_REGEX,
            ConstraintDescription=INVALID_CIDR_IP_MSG,
        ))

        self.PublicSubnet1 = t.add_parameter(Parameter(
            "PublicSubnet1",
            Default="10.0.10.0/24",
            Type="String",
            Description=(
                "Address range for a public subnet to be created in AZ1."),
            AllowedPattern=VALID_CIDR_IP_REGEX,
            ConstraintDescription=INVALID_CIDR_IP_MSG,
        ))

        self.PublicSubnet2 = t.add_parameter(Parameter(
            "PublicSubnet2",
            Default="10.0.20.0/24",
            Type="String",
            Description=(
                "Address range for a public subnet to be created in AZ2."),
            AllowedPattern=VALID_CIDR_IP_REGEX,
            ConstraintDescription=INVALID_CIDR_IP_MSG,
        ))

        self.PrivateSubnet1 = t.add_parameter(Parameter(
            "PrivateSubnet1",
            Default="10.0.11.0/24",
            Type="String",
            Description=(
                "Address range for a public subnet to be created in AZ1."),
            AllowedPattern=VALID_CIDR_IP_REGEX,
            ConstraintDescription=INVALID_CIDR_IP_MSG,
        ))

        self.PrivateSubnet2 = t.add_parameter(Parameter(
            "PrivateSubnet2",
            Default="10.0.21.0/24",
            Type="String",
            Description=(
                "Address range for a public subnet to be created in AZ2."),
            AllowedPattern=VALID_CIDR_IP_REGEX,
            ConstraintDescription=INVALID_CIDR_IP_MSG,
        ))

        self.AvailabilityZone1 = t.add_parameter(Parameter(
            "AvailabilityZone1",
            Default="eu-west-1a",
            Type="AWS::EC2::AvailabilityZone::Name",
            Description="First AZ to use for PublicSubnet1/PrivateSubnet1.",
        ))

        self.AvailabilityZone2 = t.add_parameter(Parameter(
            "AvailabilityZone2",
            Default="eu-west-1b",
            Type="AWS::EC2::AvailabilityZone::Name",
            Description="Second AZ to use for PublicSubnet2/PrivateSubnet2.",
        ))

    def add_resource(self):
        t = self.template

        self.PublicRouteTable = t.add_resource(ec2.RouteTable(
            "PublicRouteTable",
            VpcId=Ref("VPC"),
            Tags=Tags(
                Application=Ref("AWS::StackName"),
                Network="Public",
                Environment=Ref(self.Environment),
                Name=Join("-", ["RT-PU-1", Ref(self.Project)]),
            ),
        ))

        self.GatewayToInternet = t.add_resource(ec2.VPCGatewayAttachment(
            "GatewayToInternet",
            VpcId=Ref("VPC"),
            InternetGatewayId=Ref("InternetGateway"),
        ))

        self.PubSubnet1 = t.add_resource(ec2.Subnet(
            "PubSubnet1",
            Tags=Tags(
                Application=Ref("AWS::StackName"),
                Environment=Ref(self.Environment),
                Network="Public",
                Name=Join("-", ["NT-PU-1", Ref(self.Project)]),
            ),
            VpcId=Ref("VPC"),
            CidrBlock=Ref(self.PublicSubnet1),
            AvailabilityZone=Ref(self.AvailabilityZone1),
            MapPublicIpOnLaunch=True,
        ))

        self.PubSubnet2 = t.add_resource(ec2.Subnet(
            "PubSubnet2",
            Tags=Tags(
                Application=Ref("AWS::StackName"),
                Environment=Ref(self.Environment),
                Network="Public",
                Name=Join("-", ["NT-PU-2", Ref(self.Project)]),
            ),
            VpcId=Ref("VPC"),
            CidrBlock=Ref(self.PublicSubnet2),
            AvailabilityZone=Ref(self.AvailabilityZone2),
            MapPublicIpOnLaunch=True,
        ))

        self.PriSubnet2 = t.add_resource(ec2.Subnet(
            "PriSubnet2",
            Tags=Tags(
                Application=Ref("AWS::StackName"),
                Environment=Ref(self.Environment),
                Network="Private",
                Name=Join("-", ["NT-PR-2", Ref(self.Project)]),
            ),
            VpcId=Ref("VPC"),
            CidrBlock=Ref(self.PrivateSubnet2),
            AvailabilityZone=Ref(self.AvailabilityZone2),
        ))

        self.PriSubnet1 = t.add_resource(ec2.Subnet(
            "PriSubnet1",
            Tags=Tags(
                Application=Ref("AWS::StackName"),
                Environment=Ref(self.Environment),
                Network="Private",
                Name=Join("-", ["NT-PR-1", Ref(self.Project)]),
            ),
            VpcId=Ref("VPC"),
            CidrBlock=Ref(self.PrivateSubnet1),
            AvailabilityZone=Ref(self.AvailabilityZone1),
        ))

        self.PrivateRouteTable2 = t.add_resource(ec2.RouteTable(
            "PrivateRouteTable2",
            VpcId=Ref("VPC"),
            Tags=Tags(
                Application=Ref("AWS::StackName"),
                Environment=Ref(self.Environment),
                Network="Private",
                Name=Join("-", ["RT-PR-2", Ref(self.Project)]),
            ),
        ))

        self.PublicRoute = t.add_resource(ec2.Route(
            "PublicRoute",
            GatewayId=Ref("InternetGateway"),
            DestinationCidrBlock="0.0.0.0/0",
            RouteTableId=Ref(self.PublicRouteTable),
        ))

        self.PrivateRouteTable1 = t.add_resource(ec2.RouteTable(
            "PrivateRouteTable1",
            VpcId=Ref("VPC"),
            Tags=Tags(
                Application=Ref("AWS::StackName"),
                Environment=Ref(self.Environment),
                Network="Private",
                Name=Join("-", ["RT-PR-1", Ref(self.Project)]),
            ),
        ))

        self.PriSubnet2RTAssoc = t.add_resource(ec2.SubnetRouteTableAssociation(
            "PriSubnet2RTAssoc",
            SubnetId=Ref(self.PriSubnet2),
            RouteTableId=Ref(self.PrivateRouteTable2),
        ))

        self.InternetGateway = t.add_resource(ec2.InternetGateway(
            "InternetGateway",
            Tags=Tags(
                Application=Ref("AWS::StackName"),
                Environment=Ref(self.Environment),
                Network="Public",
                Name=Join("-", ["IGW", Ref(self.Project)]),
            ),
        ))

        self.VPC = t.add_resource(ec2.VPC(
            "VPC",
            CidrBlock=Ref(self.VpcCidr),
            EnableDnsSupport=True,
            EnableDnsHostnames=True,
            Tags=Tags(
                Name=Join("-", ["VPC", Ref(self.Project)]),
                Environment=Ref(self.Environment),
                Application=Ref("AWS::StackName"),
            ),
        ))

        self.PubSubnet2RTAssoc = t.add_resource(ec2.SubnetRouteTableAssociation(
            "PubSubnet2RTAssoc",
            SubnetId=Ref(self.PubSubnet2),
            RouteTableId=Ref(self.PublicRouteTable),
        ))

        self.PubSubnet1RTAssoc = t.add_resource(ec2.SubnetRouteTableAssociation(
            "PubSubnet1RTAssoc",
            SubnetId=Ref(self.PubSubnet1),
            RouteTableId=Ref(self.PublicRouteTable),
        ))

        self.PriSubnet1RTAssoc = t.add_resource(ec2.SubnetRouteTableAssociation(
            "PriSubnet1RTAssoc",
            SubnetId=Ref(self.PriSubnet1),
            RouteTableId=Ref(self.PrivateRouteTable1),
        ))

    def add_outputs(self):
        t = self.template

        self.InternetGateway = t.add_output(Output(
            "InternetGatewayID",
            Description="InternetGatewayID",
            Value=Join("", [Ref(self.InternetGateway)]),
        ))

        self.VpcId = t.add_output(Output(
            "VpcId",
            Description="VPC ID",
            Value=Join("", [Ref(self.VPC)]),
        ))

        self.PublicRouteTable1 = t.add_output(Output(
            "PrivateRouteTable1",
            Description="Private Route Table1 ID.",
            Value=Ref(self.PrivateRouteTable1),
        ))

        self.PublicRouteTable2 = t.add_output(Output(
            "PrivateRouteTable2",
            Description="Private Route Table2 ID.",
            Value=Ref(self.PrivateRouteTable2),
        ))

        self.PublicRouteTable = t.add_output(Output(
            "PublicRouteTable",
            Description="Public Route Table.",
            Value=Join("", [Ref(self.PublicRouteTable)]),
        ))

        self.PublicSubnet1ID = t.add_output(Output(
            "PublicSubnet1ID",
            Description="Public Subnet 1 ID",
            Value=Join("", [Ref(self.PubSubnet1)]),
        ))

        self.PublicSubnet2ID = t.add_output(Output(
            "PublicSubnet2ID",
            Description="Public Subnet 2 ID",
            Value=Join("", [Ref(self.PubSubnet2)]),
        ))

        self.PrivateSubnet1ID = t.add_output(Output(
            "PrivateSubnet1ID",
            Description="Private Subnet 1 ID",
            Value=Join("", [Ref(self.PriSubnet1)]),
        ))

        self.PrivateSubnet2ID = t.add_output(Output(
            "PrivateSubnet2ID",
            Description="Private Subnet 2 ID",
            Value=Join("", [Ref(self.PriSubnet2)]),
        ))

        t.add_output(Output(
            "Environment",
            Description="Environment",
            Value=Ref(self.Environment),
        ))


def sceptre_handler(sceptre_user_data):
    return Vpc(sceptre_user_data).template.to_json()

if __name__ == '__main__':
    print (sceptre_handler())
