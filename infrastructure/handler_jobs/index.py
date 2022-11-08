def handler(event, context):
    rk = event["routeKey"]
    if rk == "POST /jobs":
        return {
            "statusCode": 200,
            "body": "Job created.",
        }
    elif rk == "GET /jobs/{id}":
        return {
            "statusCode": 200,
            "body": f"Job ID: {event['pathParameters']['id']}",
        }
    elif rk == "POST /jobs/{id}/complete":
        return {
            "statusCode": 200,
            "body": f"Job {event['pathParameters']['id']} completed.",
        }
    else:
        return {
            "statusCode": 400,
            "body": f"Unsupported route: {rk}.",
        }
