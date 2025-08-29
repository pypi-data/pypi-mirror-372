# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Optional

import pymongo
import pymongo.read_concern
import pymongo.read_preferences
import pymongo.write_concern
from pymongo.client_session import ClientSession

from dyff.schema import ids
from dyff.schema.platform import Account, APIKey, Identity
from dyff.storage import timestamp
from dyff.storage.backend.base.auth import AuthBackend
from dyff.storage.config import config
from dyff.storage.exceptions import EntityExistsError


class MongoDBAuthBackend(AuthBackend):
    def __init__(self):
        connection_string = config.api.auth.mongodb.connection_string
        self._client = pymongo.MongoClient(connection_string.get_secret_value())

        # Interact with the database in a way that gives strong consistency
        # (These are currently the default settings; I prefer to be explicit)
        self._accounts_db = self._client.get_database(
            config.api.auth.mongodb.database,
            read_concern=pymongo.read_concern.ReadConcern("majority"),
            read_preference=pymongo.ReadPreference.PRIMARY,
            write_concern=pymongo.write_concern.WriteConcern("majority", wtimeout=5000),
        )

    def _get_account(
        self,
        *,
        id: Optional[str] = None,
        name: Optional[str] = None,
        identity: Optional[Identity] = None,
        session: Optional[ClientSession] = None,
    ) -> Optional[Account]:
        filter = {}
        if id is not None:
            filter["_id"] = id
        if name is not None:
            filter["name"] = name
        if identity is not None:
            identity_dict = identity.model_dump(mode="json")
            for identity_key, identity_value in identity_dict.items():
                if identity_value is not None:
                    filter[f"identity.{identity_key}"] = identity_value
        if len(filter) == 0:
            raise ValueError("must specify at least one of {id, name, identity}")
        result = self._accounts_db.accounts.find_one(filter, session=session)
        if result:
            result = dict(result)
            result["id"] = result["_id"]
            del result["_id"]
            return Account.parse_obj(result)
        return None

    def _insert_account(
        self, account: Account, *, session: Optional[ClientSession] = None
    ) -> None:
        d = account.model_dump(mode="json")
        d["_id"] = d["id"]
        del d["id"]
        self._accounts_db.accounts.insert_one(d, session=session)

    def create_account(self, name: str, identity: Optional[Identity] = None) -> Account:
        """Create a new Account.

        Parameters:
        name: A unique human-readable name
        identity: Identity from an external identity provider.

        Returns:
        Entity representing the Account.
        """
        identity = identity or Identity()
        duplicate = self._get_account(name=name, identity=identity)
        if duplicate is not None:
            raise EntityExistsError("duplicate account name or identity")
        id = ids.generate_entity_id()
        account = Account(
            id=id, name=name, identity=identity, creationTime=timestamp.now()
        )
        self._insert_account(account)
        return account

    def delete_account(self, account_id: str):
        """Delete an Account.

        Parameters:
        account_id: The unique identifier of the Account.
        """
        raise NotImplementedError()

    def get_account(
        self,
        *,
        id: Optional[str] = None,
        name: Optional[str] = None,
        identity: Optional[Identity] = None,
    ) -> Optional[Account]:
        """Get an Account by ID, identity, or name.

        Parameters:
        id: The unique identifier of the Account.
        name: The unique name of the Account.
        identity: Unique identifier of the Account according to a third-party
          identity provider. It is an error to set more than one identity.
        """
        return self._get_account(id=id, name=name, identity=identity)

    def add_api_key(self, account_id: str, api_key: APIKey) -> None:
        """Add a new APIKey to an Account.

        Raises ``ValueError`` if an APIKey with the same ID already exists.

        Parameters:
        account_id: The unique identifier of the Account.
        api_key: The new API key.
        """
        account = self._get_account(id=account_id)
        if account is None:
            raise ValueError(f"no Account with .id {account_id}")
        if any(account_key.id == api_key.id for account_key in account.apiKeys):
            raise ValueError(f"APIKey with .id {api_key.id} already exists")
        # Don't have to translate APIKey.id because APIKey isn't a
        # top-level entity
        self._accounts_db.accounts.update_one(
            {"_id": account_id}, {"$push": {"apiKeys": api_key.model_dump(mode="json")}}
        )

    def revoke_api_key(self, account_id: str, api_key_id: str) -> None:
        """Revoke an APIKey associated with an Account.

        Parameters:
        account_id: The unique identifier of the Account.
        api_key: The unique identifier of the APIKey.
        """
        account = self._get_account(id=account_id)
        if account is None:
            raise ValueError(f"no Account with .id {account_id}")
        filtered = [api_key for api_key in account.apiKeys if api_key.id != api_key_id]
        if len(filtered) == len(account.apiKeys):
            raise ValueError(f"no APIKey with .id {api_key_id} in account")
        # Don't have to translate APIKey.id because APIKey isn't a
        # top-level entity
        self._accounts_db.accounts.update_one(
            {"_id": account_id},
            {"$set": {"apiKeys": [key.model_dump(mode="json") for key in filtered]}},
        )

    def revoke_all_api_keys(self, account_id: str) -> None:
        """Revoke all API keys for the given Account.

        Parameters:
        account_id: The unique identifier of the Account.
        """
        result = self._accounts_db["accounts"].update_one(
            {"_id": account_id}, {"$set": {"apiKeys": []}}
        )
        if result.matched_count != 1:
            raise ValueError(f"no Account with .id {account_id}")

    def get_api_key(self, account_id: str, api_key_id: str) -> Optional[APIKey]:
        """Get an APIKey associated with an Account by ID.

        Parameters:
        account_id: The unique identifier of the Account.
        api_key_id: The unique identifier of the APIKey.
        """
        api_keys = self.get_all_api_keys(account_id)
        for api_key in api_keys:
            if api_key.id == api_key_id:
                return api_key
        return None

    def get_all_api_keys(self, account_id: str) -> list[APIKey]:
        """Get the API keys associated with an Account.

        Parameters:
        account_id: The unique identifier of the Account.
        """
        account = self._get_account(id=account_id)
        if account is None:
            raise ValueError(f"no Account with .id {account_id}")
        account = Account.parse_obj(account)
        return account.apiKeys
