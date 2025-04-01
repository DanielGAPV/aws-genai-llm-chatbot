# Deploying the Chatbot on your local machine

## Environment setup
If you are using a local machine, verify that your environment satisfies the following prerequisites:

You have:

1. An AWS Account
2. An IAM User with **AdministratorAccess** policy granted (for production, it's recommended to restrict access as needed)
3. [NodeJS 18 or 20](https://nodejs.org/en/download/) installed
4. [AWS CLI](https://aws.amazon.com/cli/) installed and configured to use with your AWS account
5. [AWS CDK CLI](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) installed
6. [Docker](https://docs.docker.com/get-docker/) installed
    - N.B. [`buildx`](https://github.com/docker/buildx) is also required. For Windows and macOS `buildx` is included in [Docker Desktop](https://docs.docker.com/desktop/)
7. [Python 3+](https://www.python.org/downloads/) installed

## Deployment
Before you start, please read the [precautions](docs/documentation/precautions.md) and [security](docs/documentation/security.md) pages.

Make sure you have set up your AWS credentials with `aws configure`

**Step 1.** Clone the repository.
```bash
git clone https://github.com/DanielGAPV/aws-genai-llm-chatbot.git
```

**Step 2.** Move into the cloned repository.
```bash
cd aws-genai-llm-chatbot.git
```

**Step 3.** Install the project dependencies and build the project.
```bash
npm ci && npm run build
```

**Step 4.** (Optional) Run the unit tests.
```bash
npm run test && pip install -r pytest_requirements.txt && pytest tests
```

**Step 5.** Once done, run the configuration command to help you set up the solution with the features you need
```bash
npm run config
```

You'll be prompted to configure the different aspects of the solution, such as:
- The LLMs or MLMs to enable (supports all models provided by Bedrock that [were enabled](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) along with SageMaker hosted Idefics, FalconLite, Mistral, etc.).
- Setup of the RAG system: engine selection (i.e. Aurora w/ pgvector, OpenSearch, Kendra).
- Embeddings selection.
- Limit accessibility to website and backend to VPC (private chatbot).
- Add existing Amazon Kendra indices as RAG sources.

For more details about the options, please refer to the [configuration page](docs/guide/config.md)

When done, answer `Y` to create or update your configuration.

![sample](docs/guide/assets/magic-config-sample.gif "CLI sample")

Your configuration is now stored under `bin/config.json`. You can re-run the `npm run config` command as needed to update your `config.json`

**Step 6.** (Optional) Bootstrap AWS CDK on the target account and region

> **Note**: This is required if you have never used AWS CDK on this account and region combination. ([More information on CDK bootstrapping](https://docs.aws.amazon.com/cdk/latest/guide/cli.html#cli-bootstrap)).

```bash
npm run cdk bootstrap aws://{targetAccountId}/{targetRegion}
```

You can now deploy by running:

```bash
npm run cdk deploy
```

> **Note**: This step duration can vary greatly, depending on the Constructs you are deploying.

You can view the progress of your CDK deployment in the [CloudFormation console](https://console.aws.amazon.com/cloudformation/home) in the selected region.

**Step 7.** Once deployed, take note of the `User Interface`, `User Pool` and, if you want to interact with 3P models providers, the `Secret` where to store `API_KEYS` to access 3P model providers.

```bash
...
Outputs:
GenAIChatBotStack.UserInterfaceUserInterfaceDomanNameXXXXXXXX = dxxxxxxxxxxxxx.cloudfront.net
GenAIChatBotStack.AuthenticationUserPoolLinkXXXXX = https://xxxxx.console.aws.amazon.com/cognito/v2/idp/user-pools/xxxxx_XXXXX/users?region=xxxxx
GenAIChatBotStack.ApiKeysSecretNameXXXX = ApiKeysSecretName-xxxxxx
...
```

**Step 8.** Open the generated **Cognito User Pool** Link from outputs above i.e. `https://xxxxx.console.aws.amazon.com/cognito/v2/idp/user-pools/xxxxx_XXXXX/users?region=xxxxx`

**Step 9.** Add a user that will be used to log into the web interface. 

**Step 10.** Assign the admin role to the user.

For more information, please refer to [the access control page](docs/documentation/access-control.md)

**Step 11.** Open the `User Interface` Url for the outputs above, i.e. `dxxxxxxxxxxxxx.cloudfront.net`.

**Step 12.** Login with the user created in **Step 8** and follow the instructions.

**Step 13.** (Optional) Run the integration tests
The tests require to be authenticated against your AWS Account because it will create cognito users. In addition, the tests will use `anthropic.claude-instant-v1` (Claude Instant), `anthropic.claude-3-haiku-20240307-v1:0` (Claude 3 Haiku), `amazon.titan-embed-text-v1` (Titan Embeddings G1 - Text) and `amazon.nova-canvas-v1:0` (Amazon Nova Canvas) which need to be enabled in Bedrock, 1 workspace engine and the SageMaker default models.

To run the tests (Replace the url with the one you used in the steps above)
```bash
REACT_APP_URL=https://dxxxxxxxxxxxxx.cloudfront.net pytest integtests/ --ignore integtests/user_interface -n 3 --dist=loadfile 
```
To run the UI tests, you will fist need to download and run [geckodriver](https://github.com/mozilla/geckodriver)
```bash
REACT_APP_URL=https://dxxxxxxxxxxxxx.cloudfront.net pytest integtests/user_interface 
```

## Monitoring

Once the deployment is complete, a [Amazon CloudWatch Dashboard](https://console.aws.amazon.com/cloudwatch) will be available in the selected region to monitor the usage of the resources.

For more information, please refer to [the monitoring page](docs/documentation/monitoring.md)

## Run user interface locally

To experiment with changes to the the user interface, you can run the interface locally. See the instructions in the README file of the [`lib/user-interface/react-app`](lib/user-interface/react-app/README.md) folder.

## Clean up

You can remove the stacks and all the associated resources created in your AWS account by running the following command:

```bash
npx cdk destroy
```

> **Note**: Depending on which resources have been deployed. Destroying the stack might take a while, up to 45m. If the deletion fails multiple times, please manually delete the remaining stack's ENIs; you can filter ENIs by VPC/Subnet/etc using the search bar [here](https://console.aws.amazon.com/ec2/home#NIC) in the AWS console) and re-attempt a stack deletion.