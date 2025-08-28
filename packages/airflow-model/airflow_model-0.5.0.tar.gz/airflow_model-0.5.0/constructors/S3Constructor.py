import logging
from models.S3Model import S3Model
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

class S3Constructor(S3Model):
    """
    A constructor class to perform S3 operations using the parameters
    defined in S3Model. Supports common operations like upload, download,
    list, and delete.
    """
    
    def s3constructor(self):
        """
        Executes the S3 operation defined in self.operation using S3Hook.

        Returns:
            Any: The result of the S3 operation (e.g., file content, list of keys).
        """
        try:
            hook = S3Hook(aws_conn_id=self.aws_conn_id)

            if self.operation.lower() == 'upload':
                hook.load_file(
                    filename=self.local_path,
                    key=self.key,
                    bucket_name=self.bucket_name,
                    replace=True
                )
                logging.info(f"File {self.local_path} uploaded to {self.bucket_name}/{self.key}")

            elif self.operation.lower() == 'download':
                hook.download_file(
                    key=self.key,
                    bucket_name=self.bucket_name,
                    local_path=self.local_path
                )
                logging.info(f"File {self.bucket_name}/{self.key} downloaded to {self.local_path}")

            elif self.operation.lower() == 'list':
                keys = hook.list_keys(bucket_name=self.bucket_name, prefix=self.key)
                logging.info(f"Keys in {self.bucket_name}/{self.key}: {keys}")
                return keys

            elif self.operation.lower() == 'delete':
                hook.delete_objects(bucket=self.bucket_name, keys=[self.key])
                logging.info(f"File {self.bucket_name}/{self.key} deleted")

            else:
                logging.warning(f"Unsupported operation: {self.operation}")

        except Exception as erro:
            logging.error("Error executing S3 operation: %s", erro)
            return None
