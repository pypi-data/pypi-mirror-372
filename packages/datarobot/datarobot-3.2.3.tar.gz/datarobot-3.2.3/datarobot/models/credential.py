#
# Copyright 2021-2022 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from __future__ import annotations

from datetime import datetime
import json
from typing import Any, Dict, List, Optional, Union

import trafaret as t
from trafaret.contrib.rfc_3339 import DateTime

from datarobot._compat import String
from datarobot.models.api_object import APIObject
from datarobot.utils import pagination, rawdict


class Credential(APIObject):  # pylint: disable=missing-class-docstring
    _path = "credentials/"
    _converter = t.Dict(
        {
            t.Key("name"): String(),
            t.Key("credential_id"): String(),
            t.Key("creation_date"): DateTime(),
            t.Key("credential_type"): String(),
            t.Key("description"): String(allow_blank=True),
        }
    ).allow_extra("*")

    def __init__(
        self,
        credential_id: Optional[str] = None,
        name: Optional[str] = None,
        credential_type: Optional[str] = None,
        creation_date: Optional[datetime] = None,
        description: Optional[str] = None,
    ) -> None:
        self.credential_id = credential_id
        self.name = name
        self.credential_type = credential_type
        self.creation_date = creation_date
        self.description = description

    @classmethod
    def list(cls) -> List[Credential]:
        """
        Returns list of available credentials.

        Returns
        -------
        credentials : list of Credential instances
            contains a list of available credentials.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> data_sources = dr.Credential.list()
            >>> data_sources
            [
                Credential('5e429d6ecf8a5f36c5693e03', 'my_s3_cred', 's3'),
                Credential('5e42cc4dcf8a5f3256865840', 'my_jdbc_cred', 'jdbc'),
            ]
        """

        return [
            cls.from_server_data(item) for item in pagination.unpaginate(cls._path, {}, cls._client)
        ]

    @classmethod
    def get(cls, credential_id: str) -> Credential:
        """
        Gets the Credential.

        Parameters
        ----------
        credential_id : str
            the identifier of the credential.

        Returns
        -------
        credential : Credential
            the requested credential.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> cred = dr.Credential.get('5a8ac9ab07a57a0001be501f')
            >>> cred
            Credential('5e429d6ecf8a5f36c5693e03', 'my_s3_cred', 's3'),
        """
        return cls.from_location(f"{cls._path}{credential_id}/")

    def delete(self) -> None:
        """
        Deletes the Credential the store.

        Parameters
        ----------
        credential_id : str
            the identifier of the credential.

        Returns
        -------
        credential : Credential
            the requested credential.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> cred = dr.Credential.get('5a8ac9ab07a57a0001be501f')
            >>> cred.delete()
        """
        self._client.delete(f"{self._path}{self.credential_id}/")

    @classmethod
    def create_basic(
        cls,
        name: str,
        user: str,
        password: str,
        description: Optional[str] = None,
    ) -> Credential:
        """
        Creates the credentials.

        Parameters
        ----------
        name : str
            the name to use for this set of credentials.
        user : str
            the username to store for this set of credentials.
        password : str
            the password to store for this set of credentials.
        description : str, optional
            the description to use for this set of credentials.

        Returns
        -------
        credential : Credential
            the created credential.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> cred = dr.Credential.create_basic(
            ...     name='my_basic_cred',
            ...     user='username',
            ...     password='password',
            ... )
            >>> cred
            Credential('5e429d6ecf8a5f36c5693e03', 'my_basic_cred', 'basic'),
        """
        payload = {
            "name": name,
            "credentialType": "basic",
            "user": user,
            "password": password,
            "description": description,
        }
        return cls.from_server_data(cls._client.post(cls._path, data=payload).json())

    @classmethod
    def create_oauth(
        cls,
        name: str,
        token: str,
        refresh_token: str,
        description: Optional[str] = None,
    ) -> Credential:
        """
        Creates the OAUTH credentials.

        Parameters
        ----------
        name : str
            the name to use for this set of credentials.
        token: str
            the OAUTH token
        refresh_token: str
            The OAUTH token
        description : str, optional
            the description to use for this set of credentials.

        Returns
        -------
        credential : Credential
            the created credential.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> cred = dr.Credential.create_oauth(
            ...     name='my_oauth_cred',
            ...     token='XXX',
            ...     refresh_token='YYY',
            ... )
            >>> cred
            Credential('5e429d6ecf8a5f36c5693e03', 'my_oauth_cred', 'oauth'),
        """
        payload = {
            "name": name,
            "credentialType": "oauth",
            "token": token,
            "refreshToken": refresh_token,
            "description": description,
        }
        return cls.from_server_data(cls._client.post(cls._path, data=payload).json())

    @classmethod
    def create_s3(
        cls,
        name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Credential:
        """
        Creates the S3 credentials.

        Parameters
        ----------
        name : str
            the name to use for this set of credentials.
        aws_access_key_id : str, optional
            the AWS access key id.
        aws_secret_access_key : str, optional
            the AWS secret access key.
        aws_session_token : str, optional
            the AWS session token.
        description : str, optional
            the description to use for this set of credentials.

        Returns
        -------
        credential : Credential
            the created credential.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> cred = dr.Credential.create_s3(
            ...     name='my_s3_cred',
            ...     aws_access_key_id='XXX',
            ...     aws_secret_access_key='YYY',
            ...     aws_session_token='ZZZ',
            ... )
            >>> cred
            Credential('5e429d6ecf8a5f36c5693e03', 'my_s3_cred', 's3'),
        """
        payload = {
            "name": name,
            "credentialType": "s3",
            "awsAccessKeyId": aws_access_key_id,
            "awsSecretAccessKey": aws_secret_access_key,
            "awsSessionToken": aws_session_token,
            "description": description,
        }
        return cls.from_server_data(cls._client.post(cls._path, data=payload).json())

    @classmethod
    def create_azure(
        cls,
        name: str,
        azure_connection_string: str,
        description: Optional[str] = None,
    ) -> Credential:
        """
        Creates the Azure storage credentials.

        Parameters
        ----------
        name : str
            the name to use for this set of credentials.
        azure_connection_string : str
            the Azure connection string.
        description : str, optional
            the description to use for this set of credentials.

        Returns
        -------
        credential : Credential
            the created credential.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> cred = dr.Credential.create_azure(
            ...     name='my_azure_cred',
            ...     azure_connection_string='XXX',
            ... )
            >>> cred
            Credential('5e429d6ecf8a5f36c5693e03', 'my_azure_cred', 'azure'),
        """
        payload = {
            "name": name,
            "credentialType": "azure",
            "azureConnectionString": azure_connection_string,
            "description": description,
        }
        return cls.from_server_data(cls._client.post(cls._path, data=payload).json())

    def __repr__(self) -> str:
        return "{}('{}', '{}', '{}')".format(
            self.__class__.__name__,
            self.credential_id,
            self.name,
            self.credential_type,
        )

    @classmethod
    def create_gcp(
        cls,
        name: str,
        gcp_key: Optional[Union[str, Dict[str, str]]] = None,
        description: Optional[str] = None,
    ) -> Credential:
        """
        Creates the GCP credentials.

        Parameters
        ----------
        name : str
            the name to use for this set of credentials.
        gcp_key : str | dict
            the GCP key in json format or parsed as dict.
        description : str, optional
            the description to use for this set of credentials.

        Returns
        -------
        credential : Credential
            the created credential.

        Examples
        --------
        .. code-block:: python

            >>> import datarobot as dr
            >>> cred = dr.Credential.create_gcp(
            ...     name='my_gcp_cred',
            ...     gcp_key='XXX',
            ... )
            >>> cred
            Credential('5e429d6ecf8a5f36c5693e03', 'my_gcp_cred', 'gcp'),
        """

        if isinstance(gcp_key, str):
            try:
                gcp_key = json.loads(gcp_key)
            except ValueError as e:
                raise ValueError(f"Could not parse gcp_key: {e}")

        payload = {
            "name": name,
            "credentialType": "gcp",
            "gcpKey": rawdict(gcp_key),  # type: ignore[arg-type]
            "description": description,
        }
        return cls.from_server_data(cls._client.post(cls._path, data=payload).json())

    def update(
        self, name: Optional[str] = None, description: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Update the credential values of an existing credential. Updates this object in place.

        .. versionadded:: v3.2

        Parameters
        ----------
        name : str
            The name to use for this set of credentials.
        description : str, optional
            The description to use for this set of credentials; if omitted, and name is not
            omitted, then it clears any previous description for that name.
        kwargs : Keyword arguments specific to the given credential_type that should be updated.
        """
        if name is not None:
            kwargs["name"] = name
        if description is not None:
            kwargs["description"] = description

        self._client.patch(f"{self._path}{self.credential_id}/", data=kwargs)

        if name is not None:
            self.name = name
        if description is not None:
            self.description = description


BasicCredentialsSchema = t.Dict(
    {
        t.Key("credentialType"): t.Atom("basic"),
        t.Key("user"): String(),
        t.Key("password"): String(),
    }
).allow_extra("*")

S3CredentialsSchema = t.Dict(
    {
        t.Key("credentialType"): t.Atom("s3"),
        t.Key("awsAccessKeyId", optional=True): String(),
        t.Key("awsSecretAccessKey", optional=True): String(),
        t.Key("awsSessionToken", optional=True): String(),
    }
).allow_extra("*")

OauthCredentialsSchema = t.Dict(
    {
        t.Key("credentialType"): t.Atom("oauth"),
        t.Key("oauthRefreshToken"): String(),
        t.Key("oauthClientId", optional=True): String(),
        t.Key("oauthClientSecret", optional=True): String(),
        t.Key("oauthAccessToken", optional=True): String(),
    }
).allow_extra("*")

AnyCredentialsSchema = t.Dict({t.Key("credentialType"): String()}).allow_extra("*")

CredentialDataSchema = t.Or(
    BasicCredentialsSchema, S3CredentialsSchema, OauthCredentialsSchema, AnyCredentialsSchema
)
