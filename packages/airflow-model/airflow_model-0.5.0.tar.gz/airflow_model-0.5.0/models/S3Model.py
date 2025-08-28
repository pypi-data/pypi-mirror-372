class S3Model:
    def __init__(self, default_s3_params: dict):
        """
        Represents a configurable model for interacting with Amazon S3.

        This class encapsulates the essential parameters needed to perform
        operations on S3 objects, such as uploading, downloading, listing,
        or deleting files.

        Attributes:
            
            bucket_name (str): Name of the S3 bucket. Defaults to 'default'.
            
            key (str): Path or key of the object in the S3 bucket. Defaults to ''.
            
            aws_conn_id (str): Airflow connection ID for AWS credentials. Defaults to ''.
            
            operation (str): Type of S3 operation to perform ('upload', 'download', 'list', 'delete'). Defaults to ''.
            
            local_path (str): Local file path for upload/download operations. Defaults to ''.
        """
        
        
        self.bucket_name = default_s3_params.get('bucket_name', 'default')
        
        self.key = default_s3_params.get('key', '')
        
        self.aws_conn_id = default_s3_params.get('aws_conn_id', '')
        
        self.operation = default_s3_params.get('operation', '')
        
        self.local_path = default_s3_params.get('local_path', '')
