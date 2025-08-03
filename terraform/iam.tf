resource "aws_iam_role" "ec2_cloudwatch_role" {
  name = "ec2_cloudwatch_role"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "ec2_cloudwatch_policy" {
  name = "ec2_cloudwatch_policy"
  role = aws_iam_role.ec2_cloudwatch_role.id

  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy" "dynamodb_policy" {
  name = "dynamodb_policy"
  role = aws_iam_role.ec2_cloudwatch_role.id

  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action   = [
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem",
          "dynamodb:ConditionCheckItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:GetItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:UpdateItem"
        ],
        Effect   = "Allow",
        Resource = [
          aws_dynamodb_table.users_table.arn,
          aws_dynamodb_table.posts_table.arn,
          "${aws_dynamodb_table.users_table.arn}/index/*",
          "${aws_dynamodb_table.posts_table.arn}/index/*"
        ]
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_cloudwatch_profile" {
  name = "ec2_cloudwatch_profile"
  role = aws_iam_role.ec2_cloudwatch_role.name
} 