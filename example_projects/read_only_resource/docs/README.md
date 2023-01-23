# Dotmatics::SSO::GroupInfo

Reads SSO group from AWS SSO and exposes attributes that can be used by other resources

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "Dotmatics::SSO::GroupInfo",
    "Properties" : {
        "<a href="#groupname" title="GroupName">GroupName</a>" : <i>String</i>,
        "<a href="#identitystoreid" title="IdentityStoreId">IdentityStoreId</a>" : <i>String</i>,
    }
}
</pre>

### YAML

<pre>
Type: Dotmatics::SSO::GroupInfo
Properties:
    <a href="#groupname" title="GroupName">GroupName</a>: <i>String</i>
    <a href="#identitystoreid" title="IdentityStoreId">IdentityStoreId</a>: <i>String</i>
</pre>

## Properties

#### GroupName

A GroupName that exists within AWS SSO.

_Required_: Yes

_Type_: String

_Pattern_: <code>^[\\p{L}\\p{M}\\p{S}\\p{N}\\p{P}\\t\\n\\r  \u3000]+$</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### IdentityStoreId

The Identity Store ID to help find the group name.

_Required_: Yes

_Type_: String

_Pattern_: <code>^d-[0-9a-f]{10}$|^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

## Return Values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, Ref returns the GeneratedReadOnlyId.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### GroupId

The GroupId found based on the GroupName.

#### GeneratedReadOnlyId

The generated read-only identifier.

