# slc-xmls

1. Set up conda environment
   ```
   conda env create -f environment.yml
   conda activate slc-xmls
   ```

1. Deploy the cloudformation template
   ```
   python -m pip install -r requirements.txt -t src/
   aws cloudformation package --template-file cloudformation.yml --s3-bucket <bucket> --s3-prefix cloudformation --output-template packaged.yml
   aws cloudformation deploy --stack-name <stack name> --capabilities CAPABILITY_IAM --parameter-overrides Username=<edl username> Password=<edl password> BucketName=<bucket name>
   ```

1. Generate a `slcs.txt` file with a list of all SLCs
   ```
   python inventory_slcs.py
   ```

1. Submit jobs for all SLCs in `slcs.txt`
    1. update `queue_url` in `submit_jobs.py`
    1. `python submit_jobs.py`
