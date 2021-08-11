# -*- coding: utf-8 -*-

from troposphere import Base64, FindInMap, GetAtt, Join, Output
from troposphere import Parameter, Ref, Tags
from constants import *
import troposphere.ec2 as ec2
import troposphere.route53 as route53
import troposphere.elasticloadbalancing as elb
import troposphere.cloudwatch as cloudwatch
import troposphere.autoscaling as autoscaling
import troposphere.cloudformation as cloudformation
from base import CloudformationAbstractBaseClass


class WordpressASG(CloudformationAbstractBaseClass):

    def __init__(self, sceptre_user_data):
        super(self.__class__, self).__init__()
        self.template.set_description("""Wordpress Web ASG""")
        self.add_parameters()
        self.add_mapping()
        self.add_elb()
        self.add_resources()
        self.add_outputs()

    def add_mapping(self):
        self.template.add_mapping("AWSRegion2AMI", UBUNTU_16_AMI)

    def add_parameters(self):

        t = self.template

        self.VpcId = t.add_parameter(Parameter(
            "VpcId",
            Description="VpcId",
            Type="AWS::EC2::VPC::Id",
        ))

        self.Hostname = t.add_parameter(Parameter(
            "Hostname",
            Type="String",
            Default="wordpress",
            AllowedPattern="[\\x20-\\x7E]*",
            ConstraintDescription="can contain only ASCII characters.",
        ))

        self.Domain = t.add_parameter(Parameter(
            "Domain",
            Type="String",
            Default="lab.cloudreach.com",
            AllowedPattern="[\\x20-\\x7E]*",
            ConstraintDescription="can contain only ASCII characters.",
        ))

        self.RDSEndpoint = t.add_parameter(Parameter(
            "RDSEndpoint",
            Type="String",
            AllowedPattern="[\\x20-\\x7E]*",
            ConstraintDescription="can contain only ASCII characters.",
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

        self.DBPass = t.add_parameter(Parameter(
            "DBPass",
            MinLength="8",
            Type="String",
            NoEcho=True,
            Description="The database admin account password",
            MaxLength="41",
        ))

        self.FileSystemID = t.add_parameter(Parameter(
            "FileSystemID",
            Type="String",
            Description="EFS Id fs-xxxxxxx",
            MinLength="1",
            MaxLength="64",
            ConstraintDescription="Must be a valid EFS FileSystemID",
        ))

        self.DBUser = t.add_parameter(Parameter(
            "DBUser",
            ConstraintDescription=(
                "must begin with a letter and contain only alphanumeric "
                "characters."),
            Description="Username for MySQL database access",
            MinLength="1",
            AllowedPattern="[a-zA-Z][a-zA-Z0-9]*",
            NoEcho=True,
            MaxLength="80",
            Type="String",
        ))

        self.KeyName = t.add_parameter(Parameter(
            "KeyName",
            ConstraintDescription=(
                "must be the name of an existing EC2 KeyPair."),
            Type="AWS::EC2::KeyPair::KeyName",
            Description=(
                "Name of an existing EC2 KeyPair to enable SSH access to the "
                "instances"),
        ))

        self.Subnet1 = self.template.add_parameter(Parameter(
            "Subnet1",
            Type="AWS::EC2::Subnet::Id",
            Description="Subnet1 ID",
        ))

        self.Subnet2 = self.template.add_parameter(Parameter(
            "Subnet2",
            Type="AWS::EC2::Subnet::Id",
            Description="Subnet2 ID",
        ))

        self.AvailabilityZone1 = t.add_parameter(Parameter(
            "AvailabilityZone1",
            Default="eu-west-1a",
            Type="String",
            Description="First AZ to use for PublicSubnet1/PrivateSubnet1.",
        ))

        self.AvailabilityZone2 = t.add_parameter(Parameter(
            "AvailabilityZone2",
            Default="eu-west-1b",
            Type="String",
            Description="Second AZ to use for PublicSubnet2/PrivateSubnet2.",
        ))

        self.InstanceType = t.add_parameter(Parameter(
            "InstanceType",
            Default="t2.micro",
            ConstraintDescription="must be a valid EC2 instance type.",
            Type="String",
            Description="Instance type",
        ))

        self.WebServerCapacity = t.add_parameter(Parameter(
            "WebServerCapacity",
            Description="The initial nuber of WebServer instances",
            Default="2",
            Type="Number",
            MaxValue="20",
            MinValue="1",
            ConstraintDescription="must be between 1 and 20 EC2 instances.",
        ))

        self.WebSecurityGroup = t.add_parameter(Parameter(
            "WebSecurityGroup",
            Description="Web SG",
            Type="AWS::EC2::SecurityGroup::Id",
        ))

        self.ElbSecurityGroup = t.add_parameter(Parameter(
            "ElbSecurityGroup",
            Description="ELB SG",
            Type="AWS::EC2::SecurityGroup::Id",
        ))        

    def add_elb(self):

        self.ElasticLoadBalancer = self.template.add_resource(elb.LoadBalancer(
            "ElbWeb",
            Subnets=[Ref(self.Subnet1), Ref(self.Subnet2)],
            Listeners=[{"InstancePort": "80",
                        "LoadBalancerPort": "80", "Protocol": "HTTP"}],
            CrossZone="true",
            LoadBalancerName=Join("-", ["elb", Ref(self.Project)]),
            SecurityGroups=[Ref(self.ElbSecurityGroup)],
            ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
                Enabled=True,
                Timeout=300,
            ),
            HealthCheck=elb.HealthCheck(
                HealthyThreshold="3",
                Interval="30",
                Target="HTTP:80/",
                Timeout="5",
                UnhealthyThreshold="5",
            ),
            Tags=Tags(
                Name=Join("-", ["ELB", Ref(self.Project)]),
                Environment=Ref(self.Environment),
            ),
        ))

        self.ELBcname = self.template.add_resource(route53.RecordSetType(
            "ELBcname",
            HostedZoneName=Join("", [Ref(self.Domain), "."]),
            Comment="CNAME to Web ELB",
            Name=Join(".", [Ref(self.Hostname), Ref(self.Domain)]),
            Type="CNAME",
            TTL="60",
            ResourceRecords=[GetAtt(self.ElasticLoadBalancer, "DNSName")]
        ))

    def add_resources(self):

        metadata = {
            "AWS::CloudFormation::Init": {
                "configSets": {
                    "wordpress_install": [
                        "install_wordpress"]
                },
                "install_wordpress": {
                    "packages": {
                        "apt": {
                            "apache2": [],
                            "php": [],
                            "php-mysql": [],
                            "php7.0": [],
                            "php7.0-mysql": [],
                            "libapache2-mod-php7.0": [],
                            "php7.0-cli": [],
                            "php7.0-cgi": [],
                            "php7.0-gd": [],
                            "mysql-client": [],
                            "sendmail": []
                        }
                    },
                    "sources": {
                        "/var/www/html": "http://wordpress.org/latest.tar.gz"
                    },
                    "files": {
                        "/tmp/create-wp-config": {
                            "content": {
                                "Fn::Join": ["", [
                                    "#!/bin/bash\n",
                                    "cp /var/www/html/wordpress/wp-config-sample.php /var/www/html/wordpress/wp-config.php\n",
                                    "sed -i \"s/'database_name_here'/'", Ref(
                                        self.DBName), "'/g\" wp-config.php\n",
                                    "sed -i \"s/'username_here'/'", Ref(
                                        self.DBUser), "'/g\" wp-config.php\n",
                                    "sed -i \"s/'password_here'/'", Ref(
                                        self.DBPass), "'/g\" wp-config.php\n",
                                    "sed -i \"s/'localhost'/'", Ref(
                                        self.RDSEndpoint), "'/g\" wp-config.php\n"
                                ]]
                            },
                            "mode": "000500",
                            "owner": "root",
                            "group": "root"
                        }
                    },
                    "commands": {
                        "01_configure_wordpress": {
                            "command": "/tmp/create-wp-config",
                            "cwd": "/var/www/html/wordpress"
                        }
                    }
                }
            }
        }

        self.WaitHandle = self.template.add_resource(cloudformation.WaitConditionHandle(
            "WaitHandle",
        ))

        self.WaitCondition = self.template.add_resource(cloudformation.WaitCondition(
            "WaitCondition",
            Handle=Ref(self.WaitHandle),
            Timeout="600",
            DependsOn="WebServerAutoScalingGroup",
        ))

        self.WebServerLaunchConfiguration = self.template.add_resource(autoscaling.LaunchConfiguration(
            "WebServerLaunchConfiguration",
            Metadata=metadata,
            UserData=Base64(Join("", [
                "#!/bin/bash -x\n",
                "apt-get update\n",
                "apt-get install python-pip nfs-common -y \n",
                "mkdir -p /var/www/html/\n",
                "EC2_AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)\n",
                "echo \"$EC2_AZ.", Ref(self.FileSystemID), ".efs.", Ref(
                    "AWS::Region"), ".amazonaws.com:/ /var/www/html/ nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 0 0\" >> /etc/fstab\n"
                "mount -a\n",
                "pip install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.tar.gz\n",

                # "exec > /tmp/userdata.log 2>&1\n",
                "/usr/local/bin/cfn-init -v  --stack ", Ref("AWS::StackName"),
                "         --resource WebServerLaunchConfiguration ",
                "         --configsets wordpress_install ",
                "         --region ", Ref("AWS::Region"),
                "\n",
                "/bin/mv /var/www/html/wordpress/* /var/www/html/\n",
                "/bin/rm -f /var/www/html/index.html\n",
                "/bin/rm -rf /var/www/html/wordpress/\n",
                "chown www-data:www-data /var/www/html/* -R\n",
                "/usr/sbin/service apache2 restart\n",
                "/usr/bin/curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar\n",
                "/bin/chmod +x wp-cli.phar\n",
                "/bin/mv wp-cli.phar /usr/local/bin/wp\n",
                "cd /var/www/html/\n",
                "if ! $(sudo -u www-data /usr/local/bin/wp core is-installed); then\n",
                "sudo -u www-data /usr/local/bin/wp core install ",
                "--url='", Ref(self.Hostname), ".", Ref(self.Domain), "' ",
                "--title='Cloudreach Meetup - ", Ref(
                    self.Environment), "' ",
                "--admin_user='root' ",
                "--admin_password='wordpress' ",
                "--admin_email='meetup@cloudreach.com'\n",
                "fi\n",

                "/usr/local/bin/cfn-signal -e $? --stack ", Ref(
                    "AWS::StackName"), "   -r \"Webserver setup complete\" '", Ref(self.WaitHandle), "'\n"

            ]
            )),
            ImageId=FindInMap("AWSRegion2AMI", Ref("AWS::Region"), "AMI"),
            KeyName=Ref(self.KeyName),
            SecurityGroups=[Ref(self.WebSecurityGroup)],
            InstanceType=Ref(self.InstanceType),
            AssociatePublicIpAddress=True,
        ))

        self.WebServerAutoScalingGroup = self.template.add_resource(autoscaling.AutoScalingGroup(
            "WebServerAutoScalingGroup",
            MinSize=Ref(self.WebServerCapacity),
            DesiredCapacity=Ref(self.WebServerCapacity),
            MaxSize=Ref(self.WebServerCapacity),
            VPCZoneIdentifier=[Ref(self.Subnet1), Ref(self.Subnet2)],
            AvailabilityZones=[Ref(self.AvailabilityZone1),
                               Ref(self.AvailabilityZone2)],
            Tags=autoscaling.Tags(
                Name=Join("-", [Ref(self.Project), "web", "asg"]),
                Environment=Ref(self.Environment),
                Project=Ref(self.Project),
            ),
            LoadBalancerNames=[Ref(self.ElasticLoadBalancer)],
            LaunchConfigurationName=Ref(self.WebServerLaunchConfiguration),
        ))

        self.WebServerScaleUpPolicy = self.template.add_resource(autoscaling.ScalingPolicy(
            "WebServerScaleUpPolicy",
            ScalingAdjustment="1",
            Cooldown="60",
            AutoScalingGroupName=Ref(self.WebServerAutoScalingGroup),
            AdjustmentType="ChangeInCapacity",
        ))

        self.WebServerScaleDownPolicy = self.template.add_resource(autoscaling.ScalingPolicy(
            "WebServerScaleDownPolicy",
            ScalingAdjustment="-1",
            Cooldown="60",
            AutoScalingGroupName=Ref(self.WebServerAutoScalingGroup),
            AdjustmentType="ChangeInCapacity",
        ))

        self.CPUAlarmLow = self.template.add_resource(cloudwatch.Alarm(
            "CPUAlarmLow",
            EvaluationPeriods="2",
            Dimensions=[
                cloudwatch.MetricDimension(
                    Name="AutoScalingGroupName",
                    Value=Ref(self.WebServerAutoScalingGroup)
                ),
            ],
            AlarmActions=[Ref(self.WebServerScaleDownPolicy)],
            AlarmDescription="Scale-down if CPU < 70% for 1 minute",
            Namespace="AWS/EC2",
            Period="60",
            ComparisonOperator="LessThanThreshold",
            Statistic="Average",
            Threshold="70",
            MetricName="CPUUtilization",
        ))

        self.CPUAlarmHigh = self.template.add_resource(cloudwatch.Alarm(
            "CPUAlarmHigh",
            EvaluationPeriods="2",
            Dimensions=[
                cloudwatch.MetricDimension(
                    Name="AutoScalingGroupName",
                    Value=Ref("WebServerAutoScalingGroup")
                ),
            ],
            AlarmActions=[Ref(self.WebServerScaleUpPolicy)],
            AlarmDescription="Scale-up if CPU > 50% for 1 minute",
            Namespace="AWS/EC2",
            Period="60",
            ComparisonOperator="GreaterThanThreshold",
            Statistic="Average",
            Threshold="50",
            MetricName="CPUUtilization",
        ))

    def add_outputs(self):

        self.out = self.template.add_output([
            Output("FQDN", Value=Join(
                ".", [Ref(self.Hostname), Ref(self.Domain)])),
            Output("WebSecurityGroup", Value=Ref(self.WebSecurityGroup)),
            Output("ElbSecurityGroup", Value=Ref(self.ElbSecurityGroup)),
        ])


def sceptre_handler(sceptre_user_data):
    return WordpressASG(sceptre_user_data).template.to_json()

if __name__ == '__main__':
    print (sceptre_handler())
