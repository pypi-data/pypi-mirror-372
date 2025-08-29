# patreon-python

[![Version](https://img.shields.io/pypi/v/patreon-v2.svg?style=flat)](http://pypi.python.org/pypi/patreon-v2)
[![License](https://img.shields.io/pypi/l/patreon-v2.svg?style=flat)](http://pypi.python.org/pypi/patreon-v2)
[![Python Version](https://img.shields.io/pypi/pyversions/patreon-v2.svg?style=flat)](http://pypi.python.org/pypi/patreon-v2)

> **Note**: This is a fork of the official [patreon-python](https://github.com/Patreon/patreon-python) library up to version 0.5.0. This fork has been modernized with pyproject.toml and is published as `patreon-v2` on PyPI. For legacy support, please use the [original repository](https://github.com/Patreon/patreon-python).

Interact with the Patreon API via OAuth.

Get the package from [PyPI](https://pypi.python.org/pypi/patreon-v2), typically via `pip`:

```
pip install patreon-v2
```
or
```
echo "patreon-v2" >> requirements.txt
pip install -r requirements.txt
```

Make sure that, however you install `patreon-v2`,
you install its dependencies as well (automatically handled by pip)


Step 1. Get your client_id and client_secret
---
Visit the [Patreon API Documentation](https://docs.patreon.com/#introduction) for API reference,
or go to the [Patreon Developer Portal](https://www.patreon.com/portal) to register your client.

This will provide you with a `client_id` and a `client_secret`.


Step 2. Use this library
---
e.g., in a Flask route
```python
import patreon
from flask import request
...

client_id = None      # Replace with your data
client_secret = None  # Replace with your data
creator_id = None     # Replace with your data

@app.route('/oauth/redirect')
def oauth_redirect():
    oauth_client = patreon.OAuth(client_id, client_secret)
    tokens = oauth_client.get_tokens(request.args.get('code'), '/oauth/redirect')
    access_token = tokens['access_token']

    api_client = patreon.API(access_token)
    user_response = api_client.get_identity()
    user = user_response.data()
    memberships = user.relationship('memberships')
    membership = memberships[0] if memberships and len(memberships) > 0 else None

    # pass user and membership to your view to render as needed
```

You'll notice that the `user_response` does not return raw JSON data.
Instead, it returns a [JSON:API resource object](https://github.com/Patreon/patreon-python/blob/master/patreon/jsonapi/parser.py#L4),
to simplify traversing the normalized graph data that the Patreon API returns.
Some available methods are:
* `response.data()` to get the main resource
* `response.data().attribute('full_name')` to get the `full_name` attribute from the response data
* `response.data().relationship('campaign').attribute('pledge_sum')` to get the `pledge_sum` attribute from the `campaign` resource related to the main response data
* `response.find_resource_by_type_and_id('user', '123')` to find an arbitrary resource


Step 3. (Optional) Customize your usage
---
`patreon.API` instances have methods for interacting with the API based on the routes described in the docs.
All methods include `includes` and `fields` parameters.

ie:
* `get_identity(includes=None, fields=None)`

List methods take `page_size` and `cursor` methods as well, ie:
* `get_campaigns(page_size, cursor=None, includes=None, fields=None)`

The `includes` and `fields` arguments to these methods specify
the [related resources](http://jsonapi.org/format/#fetching-includes)
and the [resource attributes](http://jsonapi.org/format/#fetching-sparse-fieldsets)
you want returned by our API, as per the [JSON:API specification](http://jsonapi.org/).
The lists of valid `includes` and `fields` arguments are provided on `patreon.schemas`.
For instance, if you wanted to request the total amount a patron has ever paid to your campaign,
which is not included by default, you could do:
```python
api_client = patreon.API(patron_access_token)
patron_response = api_client.get_identity(None, {
    'membership': patreon.schemas.member.Attributes.currently_entitled_amount_cents
})
```

`patreon.API` also has a utility method `extract_cursor`
which you can use to extract [pagination links](http://jsonapi.org/format/#fetching-pagination)
from our [json:api response documents](http://jsonapi.org):
```python
api_client = patreon.API(creator_access_token)
campaign_id = api_client.get_campaigns().data()[0].id()
memberships = []
cursor = None
while True:
    members_response = api_client.get_campaigns_by_id_members(campaign_id, 10, cursor=cursor)
    members += members_response.data()
    cursor = api_client.extract_cursor(members_response)
    if not cursor:
        break
names_and_membershipss = [{
    'full_name': member.relationship('user').attribute('full_name'),
    'amount_cents': member.attribute('amount_cents'),
} for member in members]
```


Developing
---
1. Clone this repo
1. Install dependencies
    ```
    python -m venv venv && source venv/bin/activate && pip install -e .
    ```
1. `git checkout -b my-branch-name`
1. make your edits, writing tests for any new functionality
1. make sure tests pass with `pytest`
1. `git push`
1. Open a pull request, explaining your changes (both problem and solution) clearly
