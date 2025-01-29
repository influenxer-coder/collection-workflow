# Analytics

Find inspirations and ideas to generate high performing content using trending videos from other influencers and your
own high engaging content

## Instructions

1. Install the following:
    - AWS CLI
    - SAM CLI
    - Docker

2. Login to AWS (preferably using an Admin Account)
   ```
   aws configure
   ```

3. Validate the template file
   ```
   sam validate --region <AWS Region> --lint
   ```

4. Build the project
   ```
   sam build --use-container
   ```

5. Deploy the first time using `--guided`. This can be skipped for subsequent times
   ```
   sam deploy --parameter-overrides ParameterKey1=Value1 ParameterKey2=Value2
   ```
