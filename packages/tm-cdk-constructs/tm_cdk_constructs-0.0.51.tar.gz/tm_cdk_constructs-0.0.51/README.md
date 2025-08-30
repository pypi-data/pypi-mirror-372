# CDK construct lib

Welcome to Toumoro's AWS Service Wrapper CDK Construct Library! This library is designed to make it easy and efficient to deploy and manage AWS services within your CDK projects. Whether you're provisioning infrastructure for a simple web application or orchestrating a complex cloud-native architecture, this library aims to streamline your development process by providing high-level constructs for common AWS services.

## Features

* Simplified Service Provisioning: Easily create and configure AWS services using intuitive CDK constructs.
* Best Practices Built-In: Leverage pre-configured settings and defaults based on AWS best practices to ensure reliable and secure deployments.
* Modular and Extensible: Compose your infrastructure using modular constructs, allowing for flexibility and reusability across projects.

# Contributing to CDK Construct Toumoro

[Contributing](CONTRIBUTING.md)

# Examples

[Examples](examples/README.md)

# Documentation API

[API](API.md)

# Developpement Guide

[AWS CDK Design Guidelines](https://github.com/aws/aws-cdk/blob/main/docs/DESIGN_GUIDELINES.md)

## Naming Conventions

1. *Prefixes*:

   * *Cfn* for CloudFormation resources.
   * *Fn* for constructs generating CloudFormation functions.
   * *As* for abstract classes.
   * *I* for interfaces.
   * *Vpc* for constructs related to Virtual Private Cloud.
   * *Lambda* for constructs related to AWS Lambda.
   * Example: CfnStack, FnSub, Aspects, IVpc, VpcNetwork, LambdaFunction.
2. *Construct Names*:

   * Use descriptive names that reflect the purpose of the construct.
   * CamelCase for multi-word names.
   * Avoid abbreviations unless they are widely understood.
   * Example: VpcBasic, RdsAuroraMysqlServerLess.
3. *Property Names*:

   * Follow AWS resource naming conventions where applicable.
   * Use camelCase for property names.
   * Use clear and concise names that reflect the purpose of the property.
   * Example: bucketName, vpcId, functionName.
4. *Method Names*:

   * Use verbs or verb phrases to describe actions performed by methods.
   * Use camelCase.
   * Example: addBucketPolicy, createVpc, invokeLambda.
5. *Interface Names*:

   * Interfaces begging uppercase I are reserverd to AWS CDK library.
   * Start with an prefix TmI
   * Use clear and descriptive names.
   * Example: TmIInstance, TmISecurityGroup, TmIVpc.
6. *Module Names*:

   * Use lowercase with hyphens for separating words.
   * Be descriptive but concise.
   * Follow a hierarchy if necessary, e.g., aws-cdk.aws_s3 for S3-related constructs.
   * Example: aws-cdk.aws_s3, aws-cdk.aws_ec2, aws-cdk.aws_lambda.
7. *Variable Names*:

   * Use descriptive names.
   * CamelCase for multi-word names.
   * Keep variable names concise but meaningful.
   * Example: instanceCount, subnetIds, roleArn.
8. *Enum and Constant Names*:

   * Use uppercase for constants.
   * CamelCase for multi-word names.
   * Be descriptive about the purpose of the constant or enum.
   * Example: MAX_RETRIES, HTTP_STATUS_CODES, VPC_CONFIG.
9. *File Names*:

   * Use lowercase with hyphens for separating words.
   * Reflect the content of the file.
   * Include version numbers if necessary.
   * Example: s3-bucket-stack.ts, vpc-network.ts, lambda-function.ts.
10. *Documentation Comments*:

    * Use JSDoc or similar conventions to provide clear documentation for each construct, method, property, etc.
    * Ensure that the documentation is up-to-date and accurately reflects the purpose and usage of the code.
