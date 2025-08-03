resource "aws_dynamodb_table" "users_table" {
  name           = "users"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "username"
    type = "S"
  }

  attribute {
    name = "phoneNumber"
    type = "S"
  }

  global_secondary_index {
    name            = "UsernameIndex"
    hash_key        = "username"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "PhoneNumberIndex"
    hash_key        = "phoneNumber"
    projection_type = "ALL"
  }

  tags = {
    Name = "UsersTable"
  }
}

resource "aws_dynamodb_table" "posts_table" {
  name           = "posts"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "post_id"

  attribute {
    name = "post_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "event_id"
    type = "S"
  }

  global_secondary_index {
    name            = "UserIdIndex"
    hash_key        = "user_id"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "EventIdIndex"
    hash_key        = "event_id"
    projection_type = "ALL"
  }

  tags = {
    Name = "PostsTable"
  }
} 