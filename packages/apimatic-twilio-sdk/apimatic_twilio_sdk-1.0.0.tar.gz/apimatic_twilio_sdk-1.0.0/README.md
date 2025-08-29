
# Getting Started with Twilio API Explorer

## Install the Package

The package is compatible with Python versions `3.7+`.
Install the package from PyPi using the following pip command:

```bash
pip install apimatic-twilio-sdk==1.0.0
```

You can also view the package at:
https://pypi.python.org/pypi/apimatic-twilio-sdk/1.0.0

## Test the SDK

You can test the generated SDK and the server with test cases. `unittest` is used as the testing framework and `pytest` is used as the test runner. You can run the tests as follows:

Navigate to the root directory of the SDK and run the following commands


pip install -r test-requirements.txt
pytest


## Initialize the API Client

**_Note:_** Documentation for the client can be found [here.](doc/client.md)

The following parameters are configurable for the API Client:

| Parameter | Type | Description |
|  --- | --- | --- |
| account_sid | `str` | *Default*: `'DefaultParameterValue'` |
| credential_list_sid | `str` | *Default*: `'DefaultParameterValue'` |
| workspace_sid | `str` | *Default*: `'DefaultParameterValue'` |
| service_sid | `str` | (Required) The SID of the [Service](https://www.twilio.com/docs/notify/api/service-resource) to create the resource under.<br>*Default*: `'<string>'` |
| flow_sid | `str` | (Required) The SID of the Flow with the Execution resources to read.<br>*Default*: `'<string>'` |
| environment | `Environment` | The API environment. <br> **Default: `Environment.PRODUCTION`** |
| http_client_instance | `HttpClient` | The Http Client passed from the sdk user for making requests |
| override_http_client_configuration | `bool` | The value which determines to override properties of the passed Http Client from the sdk user |
| http_call_back | `HttpCallBack` | The callback value that is invoked before and after an HTTP call is made to an endpoint |
| timeout | `float` | The value to use for connection timeout. <br> **Default: 60** |
| max_retries | `int` | The number of times to retry an endpoint call if it fails. <br> **Default: 0** |
| backoff_factor | `float` | A backoff factor to apply between attempts after the second try. <br> **Default: 2** |
| retry_statuses | `Array of int` | The http statuses on which retry is to be done. <br> **Default: [408, 413, 429, 500, 502, 503, 504, 521, 522, 524]** |
| retry_methods | `Array of string` | The http methods on which retry is to be done. <br> **Default: ['GET', 'PUT']** |
| basic_auth_credentials | [`BasicAuthCredentials`](__base_path/auth/basic-authentication.md) | The credential object for Basic Authentication |

The API client can be initialized as follows:

```python
from twilioapiexplorer.configuration import Environment
from twilioapiexplorer.http.auth.basic_auth import BasicAuthCredentials
from twilioapiexplorer.twilioapiexplorer_client import TwilioapiexplorerClient

client = TwilioapiexplorerClient(
    basic_auth_credentials=BasicAuthCredentials(
        username='username',
        password='password'
    ),
    environment=Environment.PRODUCTION,
    account_sid='DefaultParameterValue',
    credential_list_sid='DefaultParameterValue',
    workspace_sid='DefaultParameterValue',
    service_sid='<string>',
    flow_sid='<string>'
)
```

## Authorization

This API uses the following authentication schemes.

* [`basic (Basic Authentication)`](__base_path/auth/basic-authentication.md)

## List of APIs

* [Programmable SMS](doc/controllers/programmable-sms.md)
* [Phone Numbers](doc/controllers/phone-numbers.md)
* [Messaging Services](doc/controllers/messaging-services.md)
* [Caller Ids](doc/controllers/caller-ids.md)
* [Available Phone Number Countries](doc/controllers/available-phone-number-countries.md)
* [Incoming Phone Numbers](doc/controllers/incoming-phone-numbers.md)
* [SIP Domains](doc/controllers/sip-domains.md)
* [IP Access Control List](doc/controllers/ip-access-control-list.md)
* [SIP Credentials List](doc/controllers/sip-credentials-list.md)
* [Task Channels](doc/controllers/task-channels.md)
* [Task Queues](doc/controllers/task-queues.md)
* [Credential Lists](doc/controllers/credential-lists.md)
* [IP Access Control Lists](doc/controllers/ip-access-control-lists.md)
* [Origination Urls](doc/controllers/origination-urls.md)
* [Chat Services](doc/controllers/chat-services.md)
* [Chat Channels](doc/controllers/chat-channels.md)
* [Chat Credentials](doc/controllers/chat-credentials.md)
* [Chat Bindings](doc/controllers/chat-bindings.md)
* [Chat Members](doc/controllers/chat-members.md)
* [Chat Channel Webhook](doc/controllers/chat-channel-webhook.md)
* [Chat Invites](doc/controllers/chat-invites.md)
* [Chat Messages](doc/controllers/chat-messages.md)
* [Chat Roles](doc/controllers/chat-roles.md)
* [Chat Users](doc/controllers/chat-users.md)
* [Chat User Channels](doc/controllers/chat-user-channels.md)
* [Sync Documents](doc/controllers/sync-documents.md)
* [Sync Document Permissions](doc/controllers/sync-document-permissions.md)
* [Sync Services](doc/controllers/sync-services.md)
* [Sync Stream Message](doc/controllers/sync-stream-message.md)
* [Sync Lists](doc/controllers/sync-lists.md)
* [Sync Maps](doc/controllers/sync-maps.md)
* [Sync Streams](doc/controllers/sync-streams.md)
* [Wireless Usage](doc/controllers/wireless-usage.md)
* [Rate Plans](doc/controllers/rate-plans.md)
* [Composition Hooks](doc/controllers/composition-hooks.md)
* [Composition Settings](doc/controllers/composition-settings.md)
* [Room Participants](doc/controllers/room-participants.md)
* [Execution Steps](doc/controllers/execution-steps.md)
* [Flow Revisions](doc/controllers/flow-revisions.md)
* [Test Users](doc/controllers/test-users.md)
* [Message Interactions](doc/controllers/message-interactions.md)
* [Task Sid](doc/controllers/task-sid.md)
* [Field Type Sid Field Values](doc/controllers/field-type-sid-field-values.md)
* [Field Types](doc/controllers/field-types.md)
* [Model Builds](doc/controllers/model-builds.md)
* [Style Sheet](doc/controllers/style-sheet.md)
* [Access Tokens](doc/controllers/access-tokens.md)
* [Messaging Configurations](doc/controllers/messaging-configurations.md)
* [Rate Limits](doc/controllers/rate-limits.md)
* [Usage Records](doc/controllers/usage-records.md)
* [Shortcodes](doc/controllers/shortcodes.md)
* [Alphasenders](doc/controllers/alphasenders.md)
* [Conversations](doc/controllers/conversations.md)
* [Calls](doc/controllers/calls.md)
* [Recordings](doc/controllers/recordings.md)
* [Transcriptions](doc/controllers/transcriptions.md)
* [Conferences](doc/controllers/conferences.md)
* [Queues](doc/controllers/queues.md)
* [Addresses](doc/controllers/addresses.md)
* [SIP](doc/controllers/sip.md)
* [Lookups](doc/controllers/lookups.md)
* [Workspaces](doc/controllers/workspaces.md)
* [Activities](doc/controllers/activities.md)
* [Events](doc/controllers/events.md)
* [Tasks](doc/controllers/tasks.md)
* [Workers](doc/controllers/workers.md)
* [Workflows](doc/controllers/workflows.md)
* [Trunks](doc/controllers/trunks.md)
* [Recording](doc/controllers/recording.md)
* [Notify](doc/controllers/notify.md)
* [Bindings](doc/controllers/bindings.md)
* [Credentials](doc/controllers/credentials.md)
* [Services](doc/controllers/services.md)
* [Commands](doc/controllers/commands.md)
* [SI Ms](doc/controllers/si-ms.md)
* [Compositions](doc/controllers/compositions.md)
* [Rooms](doc/controllers/rooms.md)
* [Executions](doc/controllers/executions.md)
* [Flows](doc/controllers/flows.md)
* [Interactions](doc/controllers/interactions.md)
* [Participants](doc/controllers/participants.md)
* [Sessions](doc/controllers/sessions.md)
* [Assistants](doc/controllers/assistants.md)
* [Dialogues](doc/controllers/dialogues.md)
* [Webhooks](doc/controllers/webhooks.md)
* [Defaults](doc/controllers/defaults.md)
* [Sid](doc/controllers/sid.md)
* [Fields](doc/controllers/fields.md)
* [Samples](doc/controllers/samples.md)
* [Actions](doc/controllers/actions.md)
* [Queries](doc/controllers/queries.md)
* [Buckets](doc/controllers/buckets.md)
* [Challenges](doc/controllers/challenges.md)
* [Entities](doc/controllers/entities.md)
* [Factors](doc/controllers/factors.md)
* [Form](doc/controllers/form.md)
* [Notifications](doc/controllers/notifications.md)
* [Safelists](doc/controllers/safelists.md)
* [Verifications](doc/controllers/verifications.md)
* [Accounts](doc/controllers/accounts.md)
* [Applications](doc/controllers/applications.md)
* [Keys](doc/controllers/keys.md)
* [Triggers](doc/controllers/triggers.md)
* [Assets](doc/controllers/assets.md)
* [Builds](doc/controllers/builds.md)
* [Deployments](doc/controllers/deployments.md)
* [Environments](doc/controllers/environments.md)
* [Functions](doc/controllers/functions.md)
* [Logs](doc/controllers/logs.md)
* [Variables](doc/controllers/variables.md)

## SDK Infrastructure

### HTTP

* [HttpResponse](doc/http-response.md)
* [HttpRequest](doc/http-request.md)

### Utilities

* [ApiHelper](doc/api-helper.md)
* [HttpDateTime](doc/http-date-time.md)
* [RFC3339DateTime](doc/rfc3339-date-time.md)
* [UnixDateTime](doc/unix-date-time.md)

