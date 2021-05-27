# -*- coding: utf-8 -*-

from troposphere import Base64, Select, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Tags, Template
import troposphere.efs as efs
import troposphere.ec2 as ec2
from constants import *
from base import CloudformationAbstractBaseClass


class SecurityGroup(CloudformationAbstractBaseClass):

    def __init__(self, sceptre_user_data):
        super(self.__class__, self).__init__()
        self.template.add_description("""Wordpress SG""")
        self.add_parameters()
        self.add_resources()
        self.add_outputs()

    def add_parameters(self):

        self.VpcId = self.template.add_parameter(Parameter(
            "VpcId",
            Description="VpcId",
            Type="AWS::EC2::VPC::Id",
        ))

    def add_resources(self):

        t = self.template

        self.MountTargetSecurityGroup = t.add_resource(ec2.SecurityGroup(
            "MountTargetSecurityGroup",
            SecurityGroupIngress=[
                {"ToPort": "2049", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "2049"}],
            VpcId=Ref(self.VpcId),
            GroupDescription=Join("-", [Ref(self.Project), "efs", "sg"]),
            Tags=Tags(
                Name=Join("-", [Ref(self.Project), "efs", "sg"]),
                Environment=Ref(self.Environment),
                Project=Ref(self.Project),
            )
        ))

        self.ElbSecurityGroup = self.template.add_resource(ec2.SecurityGroup(
            "ElbSecurityGroup",
            SecurityGroupIngress=[
                {"ToPort": "80", "IpProtocol": "tcp",
                    "CidrIp": "0.0.0.0/0", "FromPort": "80"},
                {"ToPort": "443", "IpProtocol": "tcp",
                    "CidrIp": "0.0.0.0/0", "FromPort": "443"}
            ],
            VpcId=Ref(self.VpcId),
            GroupDescription=Join("-", [Ref(self.Project), "elb", "sg"]),
            Tags=Tags(
                Name=Join("-", [Ref(self.Project), "elb", "sg"]),
                Environment=Ref(self.Environment),
                Project=Ref(self.Project),
            )
        ))

        self.WebSecurityGroup = self.template.add_resource(ec2.SecurityGroup(
            "WebSecurityGroup",
            SecurityGroupIngress=[
                {"ToPort": "80", "IpProtocol": "tcp",
                    "CidrIp": "0.0.0.0/0", "FromPort": "80"},
                {"ToPort": "22", "IpProtocol": "tcp",
                    "CidrIp": "0.0.0.0/0", "FromPort": "22"}
            ],
            VpcId=Ref(self.VpcId),
            GroupDescription=Join("-", [Ref(self.Project), "web", "sg"]),
            Tags=Tags(
                Name=Join("-", [Ref(self.Project), "web", "sg"]),
                Environment=Ref(self.Environment),
                Project=Ref(self.Project),
            )
        ))

        self.RDSSecurityGroup = self.template.add_resource(ec2.SecurityGroup(
            "RDSSecurityGroup",
            SecurityGroupIngress=[
                {"ToPort": "3306", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "3306"}],
            VpcId=Ref(self.VpcId),
            GroupDescription=Join("-", [Ref(self.Project), "rds", "sg"]),
            Tags=Tags(
                Name=Join("-", [Ref(self.Project), "rds", "sg"]),
                Environment=Ref(self.Environment),
                Project=Ref(self.Project),
            )
        ))

    def add_outputs(self):

        self.template.add_output([
            Output("EFSsg", Value=Ref(self.MountTargetSecurityGroup)),
            Output("ELBsg", Value=Ref(self.ElbSecurityGroup)),
            Output("WEBsg", Value=Ref(self.WebSecurityGroup)),
            Output("RDSsg", Value=Ref(self.RDSSecurityGroup)),
        ])


def sceptre_handler(sceptre_user_data):
    return SecurityGroup(sceptre_user_data).template.to_json()

if __name__ == '__main__':
    print (sceptre_handler())
