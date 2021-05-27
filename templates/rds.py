from troposphere import GetAtt, Join, Output
from troposphere import Parameter, Ref, Tags
from constants import *
import troposphere.ec2 as ec2
import troposphere.rds as rds
from base import CloudformationAbstractBaseClass


class WordpressRDS(CloudformationAbstractBaseClass):

    def __init__(self, sceptre_user_data):
        super(self.__class__, self).__init__()
        self.template.add_description("Wordpress for RDS MySQL")
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

        self.MultiAZDatabase = t.add_parameter(Parameter(
            "MultiAZDatabase",
            Default="false",
            ConstraintDescription="must be either true or false.",
            Type="String",
            Description="Create a Multi-AZ MySQL Amazon RDS database instance",
            AllowedValues=["true", "false"],
        ))

        self.DatabaseSnapshot = t.add_parameter(Parameter(
            "DatabaseSnapshot",
            AllowedPattern="[a-zA-Z0-9]*",
            Default="",
            Type="String",
            ConstraintDescription="Must be alphanumeric string",
            Description="DB Snapshot (optional)",
        ))

        self.DBInstanceClass = t.add_parameter(Parameter(
            "DBInstanceClass",
            Default="db.t2.micro",
            ConstraintDescription="Must be valid RDS instance type db.xx.xxxx",
            Type="String",
            Description="The database instance type",
        ))

        self.DatabaseBackupRetentionPeriod = t.add_parameter(Parameter(
            "DatabaseBackupRetentionPeriod",
            Default="0",
            Type="Number",
            ConstraintDescription="Must be a number",
            Description="Number of dats which automatic backups are retained",
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

        self.DBAllocatedStorage = t.add_parameter(Parameter(
            "DBAllocatedStorage",
            Description="The size of the database (Gb)",
            Default="5",
            Type="Number",
            MaxValue="1024",
            MinValue="5",
            ConstraintDescription="must be between 5 and 1024Gb.",
        ))

        self.DBName = t.add_parameter(Parameter(
            "DBName",
            Type="String",
            Description="DB Name",
            Default="mydb",
            MinLength="1",
            AllowedPattern="[a-zA-Z0-9]*",
            MaxLength="64",
            ConstraintDescription="Must be alphanumeric string",
        ))

        self.DatabaseMaintenanceWindow = t.add_parameter(Parameter(
            "DatabaseMaintenanceWindow",
            AllowedPattern=(
                "[a-z][a-z][a-z]:\\d\\d:\\d\\d-[a-z][a-z][a-z]"
                ":\\d\\d:\\d\\d|^$"),
            Default="",
            Type="String",
            ConstraintDescription="Must be hh:mm-hh:mm window or blank",
            Description=(
                "Maintenance Window (leave blank for random overnight GMT, "
                "no overlap with backup)"),
        ))

        self.DatabaseIops = t.add_parameter(Parameter(
            "DatabaseIops",
            AllowedPattern="\\d*",
            Default="",
            Type="String",
            ConstraintDescription=(
                "Must be number in multiple of 1000 or blank for no IOPS"),
            Description="DB IOPS (optional, in 1000 iops increments)",
        ))

        self.DatabasePort = t.add_parameter(Parameter(
            "DatabasePort",
            Description="DB port",
            Default="3306",
            ConstraintDescription="Must be a number",
            AllowedPattern="\\d+",
            MinLength="1",
            Type="String",
        ))

        self.DBPass = t.add_parameter(Parameter(
            "DBPass",
            MinLength="8",
            Type="String",
            NoEcho=True,
            Description="The database admin account password",
            MaxLength="41",
        ))

        self.DBUser = t.add_parameter(Parameter(
            "DBUser",
            ConstraintDescription=(
                "must begin with a letter and contain only alphanumeric "
                "characters."
            ),
            Description="Username for MySQL database access",
            MinLength="1",
            AllowedPattern="[a-zA-Z][a-zA-Z0-9]*",
            NoEcho=True,
            MaxLength="80",
            Type="String",
        ))

        self.DatabaseEngineVersion = t.add_parameter(Parameter(
            "DatabaseEngineVersion",
            Default="5.6",
            MinLength="1",
            Type="String",
            ConstraintDescription="Must be a valid AWS db engine version",
            Description="Engine Version",
        ))

        self.DatabaseBackupWindow = t.add_parameter(Parameter(
            "DatabaseBackupWindow",
            AllowedPattern="\\d\\d:\\d\\d-\\d\\d:\\d\\d|^$",
            Default="",
            Type="String",
            ConstraintDescription="Must be hh:mm-hh:mm or blank",
            Description=(
                "Backup Window (leave blank for random overnight GMT, no "
                "overlap with maintenance window)"),
        ))

        self.DatabaseAllocatedStorage = t.add_parameter(Parameter(
            "DatabaseAllocatedStorage",
            Description="The allocated storage for the database",
            Default="20",
            ConstraintDescription="must be number between 5 and 1024 (gb)",
            MaxValue="1024",
            MinValue="5",
            Type="Number",
        ))

        self.DatabaseEngine = t.add_parameter(Parameter(
            "DatabaseEngine",
            Description="Engine Selection",
            Default="MySQL",
            MinLength="1",
            AllowedValues=["MySQL", "postgres"],
            ConstraintDescription="Must be a valid AWS db engine type",
            Type="String",
        ))

        self.RDSSecurityGroup = t.add_parameter(Parameter(
            "RDSSecurityGroup",
            Description="RDS SG",
            Type="AWS::EC2::SecurityGroup::Id",
        ))

    def add_resources(self):

        self.MySQLDBSubnetGroup = self.template.add_resource(rds.DBSubnetGroup(
            "MySQLDBSubnetGroup",
            SubnetIds=[Ref(self.Subnet1), Ref(self.Subnet2)],
            DBSubnetGroupDescription="MySQLDBSubnetGroup",
            Tags=Tags(
                Name=Join("-", ["DB-SUB-GRP", Ref(self.Project)]),
                Environment=Ref(self.Environment),
            ),
        ))

        self.MySQLDatabase = self.template.add_resource(rds.DBInstance(
            "MySQLDatabase",
            DBInstanceIdentifier=Join("-", ["rds", Ref(self.Project)]),
            Engine="MySQL",
            MultiAZ=Ref(self.MultiAZDatabase),
            PubliclyAccessible="false",
            MasterUsername=Ref(self.DBUser),
            MasterUserPassword=Ref(self.DBPass),
            VPCSecurityGroups=[Ref(self.RDSSecurityGroup)],
            AllocatedStorage=Ref(self.DBAllocatedStorage),
            DBInstanceClass=Ref(self.DBInstanceClass),
            DBSubnetGroupName=Ref(self.MySQLDBSubnetGroup),
            DBName=Ref(self.DBName),
            Tags=Tags(
                Name=Join("-", ["rds", Ref(self.Project)]),
                Environment=Ref(self.Environment),
                Project=Ref(self.Project),
            )
        ))

    def add_outputs(self):

        self.out = self.template.add_output([
            Output("DBUser", Value=Ref(self.DBUser)),
            Output("DBName", Value=Ref(self.DBName)),
            Output("MySQLPort", Value=GetAtt(
                self.MySQLDatabase, "Endpoint.Port")),
            Output("MySQLAddress", Value=GetAtt(
                self.MySQLDatabase, "Endpoint.Address")),
        ])


def sceptre_handler(sceptre_user_data):
    return WordpressRDS(sceptre_user_data).template.to_json()

if __name__ == '__main__':
    print (sceptre_handler())
