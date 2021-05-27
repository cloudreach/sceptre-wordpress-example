#!/usr/bin/env python
from troposphere import Template, Parameter
from constants import *
from abc import ABCMeta


class CloudformationAbstractBaseClass:

    """ Abstract base class with some common CFN functionality """

    __metaclass__ = ABCMeta

    def __init__(self):
        # Add local vars
        self.template = Template()
        self.add_mandatory_tags()

    def add_mandatory_tags(self):
        """ Add parameters for mandatory tags and naming policies """

        self.Environment = self.template.add_parameter(Parameter(
            "Environment",
            Description="Value for Environment tag",
            Type="String",
            MinLength="1",
            AllowedValues=["prod", "shared", "dev"]
        ))
        self.Project = self.template.add_parameter(Parameter(
            "Project",
            Type="String",
            Description="Project Name",
            MinLength="1",
            MaxLength="255",
            Default=PROJECT,
            AllowedPattern="[\\x20-\\x7E]*",
            ConstraintDescription="can contain only ASCII characters.",
        ))
