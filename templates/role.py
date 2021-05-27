# -*- coding: utf-8 -*-

from troposphere import GetAtt, Output
from troposphere import Ref, Template
import troposphere.iam as iam


class IamRole(object):

    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.template.add_description("""Wordpress Iam Role""")
        self.add_role()
        self.add_outputs()

    def add_role(self):

        self.Ec2Role = self.template.add_resource(iam.Role(
            "Ec2Role",
            RoleName="ec2-role",
            Policies=[iam.Policy(
                PolicyName="ec2-policy",
                PolicyDocument={"Version": "2012-10-17",
                                "Statement": [
                                    {
                                        "Action": [
                                            "ec2:DescribeInstances",
                                            "elasticloadbalancing:Describe*",
                                            "cloudwatch:ListMetrics",
                                            "cloudwatch:GetMetricStatistics",
                                            "cloudwatch:Describe*",
                                            "cloudwatch:PutMetricData",
                                            "autoscaling:Describe*"
                                        ],
                                        "Effect": "Allow",
                                        "Resource": ["*"]
                                    },
                                    {
                                        "Sid": "Stmt1456922473000",
                                        "Effect": "Allow",
                                        "Action": [
                                            "logs:CreateLogGroup",
                                            "logs:CreateLogStream",
                                            "logs:PutLogEvents",
                                            "logs:DescribeLogStreams"
                                        ],
                                        "Resource": ["arn:aws:logs:*:*:*"]
                                    }
                                ]
                                },
            )
            ],
            AssumeRolePolicyDocument={
                "Version": "2008-10-17",
                "Statement": [
                    {
                        "Action": [
                            "sts:AssumeRole"
                        ],
                        "Effect": "Allow",
                        "Principal":
                            {
                                "Service": [
                                    "ec2.amazonaws.com"
                                ]
                        }
                    }
                ]
            }
        ))

        self.inst_profile = self.template.add_resource(iam.InstanceProfile(
            "InstanceProfile",
            Roles=[Ref(self.Ec2Role)]
        ))

    def add_outputs(self):
        self.out = self.template.add_output([
            Output("Ec2Role", Value=GetAtt(self.Ec2Role, "Arn")),
            Output("InstanceProfile", Value=GetAtt(self.inst_profile, "Arn")),
        ])


def sceptre_handler(sceptre_user_data):
    return IamRole(sceptre_user_data).template.to_json()

if __name__ == '__main__':
    print (sceptre_handler())
