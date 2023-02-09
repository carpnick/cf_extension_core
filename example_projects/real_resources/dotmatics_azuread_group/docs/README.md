# Dotmatics::AzureAD::Group

Creates an Azure AD Group

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "Dotmatics::AzureAD::Group",
    "Properties" : {
        "<a href="#groupname" title="GroupName">GroupName</a>" : <i>String</i>,
        "<a href="#grouptype" title="GroupType">GroupType</a>" : <i>String</i>,
        "<a href="#groupdescription" title="GroupDescription">GroupDescription</a>" : <i>String</i>,
        "<a href="#owners" title="Owners">Owners</a>" : <i>[ <a href="owner.md">Owner</a>, ... ]</i>,
        "<a href="#credentialappclientid" title="CredentialAppClientId">CredentialAppClientId</a>" : <i>String</i>,
        "<a href="#credentialappapitoken" title="CredentialAppAPIToken">CredentialAppAPIToken</a>" : <i>String</i>,
        "<a href="#credentialtenantid" title="CredentialTenantId">CredentialTenantId</a>" : <i>String</i>,
    }
}
</pre>

### YAML

<pre>
Type: Dotmatics::AzureAD::Group
Properties:
    <a href="#groupname" title="GroupName">GroupName</a>: <i>String</i>
    <a href="#grouptype" title="GroupType">GroupType</a>: <i>String</i>
    <a href="#groupdescription" title="GroupDescription">GroupDescription</a>: <i>String</i>
    <a href="#owners" title="Owners">Owners</a>: <i>
      - <a href="owner.md">Owner</a></i>
    <a href="#credentialappclientid" title="CredentialAppClientId">CredentialAppClientId</a>: <i>String</i>
    <a href="#credentialappapitoken" title="CredentialAppAPIToken">CredentialAppAPIToken</a>: <i>String</i>
    <a href="#credentialtenantid" title="CredentialTenantId">CredentialTenantId</a>: <i>String</i>
</pre>

## Properties

#### GroupName

A name for the group

_Required_: Yes

_Type_: String

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### GroupType

Type of group to create

_Required_: Yes

_Type_: String

_Allowed Values_: <code>SECURITY</code> | <code>Microsoft365</code>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### GroupDescription

Description of the group

_Required_: Yes

_Type_: String

_Minimum Length_: <code>1</code>

_Maximum Length_: <code>1024</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Owners

The Owners of the group

_Required_: Yes

_Type_: List of <a href="owner.md">Owner</a>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

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

#### GroupId

The ID of the group

#### GeneratedId

The generated read-only identifier.

