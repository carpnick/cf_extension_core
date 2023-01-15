
import cf_extension_core as dynamo

def test_quick():
    assert dynamo.interface.DynamoDBValues.TABLE_NAME == dynamo.interface.DynamoDBValues.TABLE_NAME