# Dotmatics::AzureAD::GroupAssignment

Assigns an Azure AD Group to an Application

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "Dotmatics::AzureAD::GroupAssignment",
    "Properties" : {
        "<a href="#groupid" title="GroupId">GroupId</a>" : <i>String</i>,
        "<a href="#appname" title="AppName">AppName</a>" : <i>String</i>,
        "<a href="#approlename" title="AppRoleName">AppRoleName</a>" : <i>String</i>,
        "<a href="#credentialappclientid" title="CredentialAppClientId">CredentialAppClientId</a>" : <i>String</i>,
        "<a href="#credentialappapitoken" title="CredentialAppAPIToken">CredentialAppAPIToken</a>" : <i>String</i>,
        "<a href="#credentialtenantid" title="CredentialTenantId">CredentialTenantId</a>" : <i>String</i>
    }
}
</pre>

### YAML

<pre>
Type: Dotmatics::AzureAD::GroupAssignment
Properties:
    <a href="#groupid" title="GroupId">GroupId</a>: <i>String</i>
    <a href="#appname" title="AppName">AppName</a>: <i>String</i>
    <a href="#approlename" title="AppRoleName">AppRoleName</a>: <i>String</i>
    <a href="#credentialappclientid" title="CredentialAppClientId">CredentialAppClientId</a>: <i>String</i>
    <a href="#credentialappapitoken" title="CredentialAppAPIToken">CredentialAppAPIToken</a>: <i>String</i>
    <a href="#credentialtenantid" title="CredentialTenantId">CredentialTenantId</a>: <i>String</i>
</pre>

## Properties

#### GroupId

Azure AD Group Id

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### AppName

The Application the group should be assigned to

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### AppRoleName

The Application role the group should be assigned to.  Defaults to `User`

_Required_: No

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### CredentialAppClientId

The Client(app)-ID of the client used the authenticate to the app

_Required_: Yes

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### CredentialAppAPIToken

Secret of the `CredentialAppClientId` App (API)

_Required_: Yes

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### CredentialTenantId

The GUID of the Office 365 Tenant that the `CredentialAppClientId` is in 

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

## Return Values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, Ref returns the GeneratedId.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### AssignmentId

The Assignment ID for when the group gets assigned to the Application.

#### GeneratedId

The generated read-only identifier.

