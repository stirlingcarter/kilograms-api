import boto3
import uuid
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

class UserService:
    def __init__(self, app):
        self.logger = app.logger
        self.dynamodb = boto3.resource('dynamodb', region_name=app.config['AWS_REGION'])
        self.table = self.dynamodb.Table('users')

    def find_user_by_phone_number(self, phone_number):
        self.logger.info(f"Querying for user with phone number: {phone_number}")
        try:
            response = self.table.query(
                IndexName='PhoneNumberIndex',
                KeyConditionExpression=Key('phoneNumber').eq(phone_number)
            )
            self.logger.debug(f"DynamoDB query response: {response}")
            items = response.get('Items', [])
            if items:
                self.logger.info(f"Found user for phone number {phone_number}")
                return items[0]
            self.logger.info(f"No user found for phone number: {phone_number}")
            return None
        except ClientError as e:
            self.logger.error(f"DynamoDB query failed for phone number {phone_number}: {e.response['Error']['Message']}")
            return None

    def find_user_by_id(self, user_id):
        self.logger.info(f"Querying for user with ID: {user_id}")
        try:
            response = self.table.get_item(Key={'user_id': user_id})
            item = response.get('Item')
            if item:
                self.logger.info(f"Found user for ID {user_id}")
                return item
            self.logger.info(f"No user found for ID: {user_id}")
            return None
        except ClientError as e:
            self.logger.error(f"DynamoDB get_item failed for user ID {user_id}: {e.response['Error']['Message']}")
            return None

    def create_user(self, phone_number):
        user_id = str(uuid.uuid4())
        self.logger.info(f"Attempting to create new user with ID {user_id} for phone number: {phone_number}")
        user = {
            'user_id': user_id,
            'phoneNumber': phone_number,
            'name': f"User {user_id[:8]}", # A default name
        }
        try:
            self.table.put_item(Item=user)
            self.logger.info(f"Successfully created user: {user}")
            # Return the full user object including what was just put into the DB
            return self.find_user_by_phone_number(phone_number)
        except ClientError as e:
            self.logger.error(f"DynamoDB put_item failed for new user with phone number {phone_number}: {e.response['Error']['Message']}")
            return None

    def update_user_otp(self, user_id, otp, otp_expiration):
        self.logger.info(f"Attempting to update OTP for user ID: {user_id}")
        try:
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression="SET otp = :otp, otp_expiration = :exp",
                ExpressionAttributeValues={
                    ':otp': otp,
                    ':exp': otp_expiration.isoformat()
                }
            )
            self.logger.info(f"Successfully updated OTP for user ID: {user_id}")
            return True
        except ClientError as e:
            self.logger.error(f"DynamoDB update_item failed for OTP on user ID {user_id}: {e.response['Error']['Message']}")
            return False
        
    def clear_user_otp(self, user_id):
        self.logger.info(f"Attempting to clear OTP for user ID: {user_id}")
        try:
            self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression="REMOVE otp, otp_expiration"
            )
            self.logger.info(f"Successfully cleared OTP for user ID: {user_id}")
            return True
        except ClientError as e:
            self.logger.error(f"DynamoDB update_item failed for clearing OTP on user ID {user_id}: {e.response['Error']['Message']}")
            return False

def initialize_user_service(app):
    return UserService(app) 