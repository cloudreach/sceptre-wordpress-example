# -*- coding: utf-8 -*-

from troposphere import Join, Output
from troposphere import Parameter, Ref, Tags
import troposphere.efs as efs
import troposphere.ec2 as ec2
from constants import *
from base import CloudformationAbstractBaseClass


class Efs(CloudformationAbstractBaseClass):

    def __init__(self, sceptre_user_data):
        super(self.__class__, self).__init__()
        self.template.add_description("""Wordpress EFS""")
        self.add_parameters()
        self.add_resources()
        self.add_outputs()

    def add_parameters(self):

        t = self.template

        self.VpcId = t.add_parameter(Parameter(
            "VpcId",
            Description="VpcId",
            Type="AWS::EC2::VPC::Id",
        ))

        self.Subnet1 = t.add_parameter(Parameter(
            "Subnet1",
            Type="AWS::EC2::Subnet::Id",
            Description="Subnet1 ID",
        ))

        self.Subnet2 = t.add_parameter(Parameter(
            "Subnet2",
            Type="AWS::EC2::Subnet::Id",
            Description="Subnet2 ID",
        ))

        self.EfsSecurityGroup = t.add_parameter(Parameter(
            "EfsSecurityGroup",
            Description="EFS SG",
            Type="AWS::EC2::SecurityGroup::Id",
        ))

        self.PerformanceMode = t.add_parameter(Parameter(
            "PerformanceMode",
            Type="String",
            Default="generalPurpose",
            Description="EFS PerformanceMode",
            AllowedValues=["generalPurpose", "maxIO"],
        ))

    def add_resources(self):

        t = self.template

        self.FileSystem = t.add_resource(efs.FileSystem(
            "FileSystem",
            PerformanceMode=Ref(self.PerformanceMode),
            FileSystemTags=Tags(
                Name=Join("-", [Ref(self.Project), "efs"]),
                Environment=Ref(self.Environment),
                Project=Ref(self.Project),
            )
        ))

        self.MountTarget1 = t.add_resource(efs.MountTarget(
            "MountTarget1",
            SubnetId=Ref(self.Subnet1),
            FileSystemId=Ref(self.FileSystem),
            SecurityGroups=[Ref(self.EfsSecurityGroup)],
        ))

        self.MountTarget2 = t.add_resource(efs.MountTarget(
            "MountTarget2",
            SubnetId=Ref(self.Subnet2),
            FileSystemId=Ref(self.FileSystem),
            SecurityGroups=[Ref(self.EfsSecurityGroup)],
        ))

    def add_outputs(self):
        t = self.template

        t.add_output(Output(
            "MountTarget1",
            Description="Mount target 1",
            Value=Ref(self.MountTarget1),
        ))

        t.add_output(Output(
            "MountTarget2",
            Description="Mount target 2",
            Value=Ref(self.MountTarget2),
        ))

        t.add_output(Output(
            "FileSystemID",
            Description="File system ID",
            Value=Ref(self.FileSystem),
        ))


def sceptre_handler(sceptre_user_data):
    return Efs(sceptre_user_data).template.to_json()

if __name__ == '__main__':
    print (sceptre_handler())
