import pickle
import yaml
import boto3

class Uploader:
    def __init__(self, model_path, config_path):
        self.model_path  = model_path
        self.config_path = config_path
        
        self.model  = self.load_model_from_file()
        self.config = self.load_configuration()

    def load_model_from_file(self):
        with open(self.model_path, "rb") as file:
            loaded_model = pickle.load(file)
        return loaded_model

    def load_configuration(self):
        with open(self.config_path, "r") as config_file:
            return yaml.safe_load(config_file)

    def upload_to_dynamodb(self):
        aws_credentials = self.config["aws"]
        dynamodb_info   = self.config["dynamodb"]

        # AWS credentials
        aws_access_key_id     = aws_credentials["access_key_id"]
        aws_secret_access_key = aws_credentials["secret_access_key"]
        region_name           = aws_credentials["region_name"]

        # DynamoDB table info
        table_name = dynamodb_info["table_name"]
        model_key  = dynamodb_info["model_key"]

        # Serialize model
        serialized_model = pickle.dumps(self.model)

        # Initialize DynamoDB client
        dynamodb = boto3.resource("dynamodb", 
                                  aws_access_key_id=aws_access_key_id, 
                                  aws_secret_access_key=aws_secret_access_key, 
                                  region_name=region_name)
        table = dynamodb.Table(table_name)

        # Upload
        table.put_item(
            Item={
                "ModelId": model_key,
                "serialized_model": serialized_model
            }
        )

        print("Model uploaded to DynamoDB successfully.")

if __name__ == "__main__":
    model_path = r"model/xgboost_31-01-2024.pkl"
    config_path = r"config.yml"

    uploader = Uploader(model_path, config_path)
    uploader.upload_to_dynamodb()
