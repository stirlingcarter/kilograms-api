import boto3
import uuid
from boto3.dynamodb.conditions import Key

class UserService:
    def __init__(self, app):
        self.logger = app.logger
        self.dynamodb = boto3.resource('dynamodb', region_name=app.config['AWS_REGION'])
        self.table = self.dynamodb.Table('users')

    def find_user_by_phone_number(self, phone_number):
        self.logger.info(f"Querying for user with phone number: {phone_number}")
        # This assumes a GSI named 'PhoneNumberIndex' exists on the 'phoneNumber' attribute.
        response = self.table.query(
            IndexName='PhoneNumberIndex',
            KeyConditionExpression=Key('phoneNumber').eq(phone_number)
        )
        items = response.get('Items', [])
        if items:
            self.logger.info(f"Found user for phone number {phone_number}: {items[0]}")
            return items[0]
        self.logger.info(f"No user found for phone number: {phone_number}")
        return None

    def create_user(self, phone_number):
        user_id = str(uuid.uuid4())
        self.logger.info(f"Creating new user with ID {user_id} for phone number: {phone_number}")
        user = {
            'user_id': user_id,
            'phoneNumber': phone_number,
            'name': f"User {user_id[:8]}", # A default name
            'otp': None,
            'otp_expiration': None
        }
        self.table.put_item(Item=user)
        self.logger.info(f"Successfully created user: {user}")
        return user

    def update_user_otp(self, user_id, otp, otp_expiration):
        self.logger.info(f"Updating OTP for user ID: {user_id}")
        self.table.update_item(
            Key={'user_id': user_id},
            UpdateExpression="SET otp = :otp, otp_expiration = :exp",
            ExpressionAttributeValues={
                ':otp': otp,
                ':exp': otp_expiration.isoformat()
            }
        )
        self.logger.info(f"Successfully updated OTP for user ID: {user_id}")
        
    def clear_user_otp(self, user_id):
        self.logger.info(f"Clearing OTP for user ID: {user_id}")
        self.table.update_item(
            Key={'user_id': user_id},
            UpdateExpression="REMOVE otp, otp_expiration"
        )
        self.logger.info(f"Successfully cleared OTP for user ID: {user_id}")

def initialize_user_service(app):
    return UserService(app) 