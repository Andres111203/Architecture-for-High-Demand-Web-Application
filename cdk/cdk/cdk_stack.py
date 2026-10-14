from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2
    # aws_sqs as sqs,
)
from constructs import Construct

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "TheVPC",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(name="public", cidr_mask=24, subnet_type=ec2.SubnetType.PUBLIC),
                ec2.SubnetConfiguration(name="private", cidr_mask=24, subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            ]
        )

        #declarando el grupo de seguridad del ALB
        alb_security_group = ec2.SecurityGroup(self, "AlbecurityGroup", vpc=vpc)
        alb_security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Just allow HTTPS traffic" )

        #declarando el grupo de seguridad de la ec2 
        my_security_group = ec2.SecurityGroup(self, "Ec2SecurityGroup", vpc=vpc)
        my_security_group.add_ingress_rule(alb_security_group, ec2.Port.tcp(80))

        asg = autoscaling.AutoScalingGroup(self, "ASG",
            vpc=vpc,
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            security_group=my_security_group,
            max_capacity=6,
            min_capacity=2

        )

        asg.scale_on_cpu_utilization(
            "scalingPolicy", 
            target_utilization_percent=70,
            disable_scale_in=False
        )

        alb = elbv2.ApplicationLoadBalancer(self, "LB",
            vpc=vpc,
            internet_facing=True,
            security_group=alb_security_group
        )

        asg.add_user_data(
            "yum update -y",
            "amazon-linux-extras install nginx1 -y",
            "systemctl start nginx",
            "systemctl enable nginx"
        )

        listener = alb.add_listener("Listener", port=80, open=False)
        listener.add_targets("Fleet", 
            port=80,
            targets=[asg]
        )



        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "CdkQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

      
